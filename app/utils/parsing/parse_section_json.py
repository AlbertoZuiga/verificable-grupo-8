import json

from app.models.evaluation import Evaluation
from app.models.evaluation_instance import EvaluationInstance
from app.models.section import Section, WeighingType
from app.models.teacher import Teacher
from app.utils import json_constants as JC



def parse_sections_json(json_data):
    data = json.loads(json_data)

    if JC.SECTIONS not in data:
        raise ValueError(f"Falta la clave '{JC.SECTIONS}' en el JSON.")

    parsed_sections = []
    parsed_evaluations = []
    parsed_instances = []

    for section_data in data[JC.SECTIONS]:
        section = _parse_section_header(section_data)
        parsed_sections.append(section)

        evaluation_data = section_data[JC.EVALUATION]
        topic_combinations = evaluation_data[JC.TOPIC_COMBINATIONS]
        topic_details = evaluation_data[JC.TOPICS]
        weighing_type = section.weighing_type

        _normalize_section_weights(weighing_type, topic_combinations)

        for topic in topic_combinations:
            evaluation, instances = _parse_evaluation(topic, topic_details, section)
            parsed_evaluations.append(evaluation)
            parsed_instances.extend(instances)

    print(
        f"[DEBUG] Parsed {len(parsed_sections)} sections, "
        f"{len(parsed_evaluations)} evaluations, and "
        f"{len(parsed_instances)} evaluation instances."
    )
    return parsed_sections, parsed_evaluations, parsed_instances


def _parse_section_header(section_data):
    _require_keys(section_data, [JC.ID, JC.COURSE_INSTANCE, JC.TEACHER_ID, JC.EVALUATION])
    _validate_teacher_exists(section_data[JC.TEACHER_ID])
    _validate_types(section_data, {JC.ID: int, JC.COURSE_INSTANCE: int, JC.TEACHER_ID: int})

    evaluation_data = section_data[JC.EVALUATION]
    _require_keys(evaluation_data, [JC.EVALUATION_TYPE, JC.TOPIC_COMBINATIONS, JC.TOPICS])
    _validate_types(
        evaluation_data, {JC.EVALUATION_TYPE: str, JC.TOPIC_COMBINATIONS: list, JC.TOPICS: dict}
    )

    weighing_type = _parse_weighing_type(evaluation_data[JC.EVALUATION_TYPE])
    return Section(
        id=section_data[JC.ID],
        code=section_data[JC.ID],
        course_instance_id=section_data[JC.COURSE_INSTANCE],
        teacher_id=section_data[JC.TEACHER_ID],
        weighing_type=weighing_type,
    )


def _normalize_section_weights(weighing_type, topic_combinations):
    if weighing_type != WeighingType.PERCENTAGE:
        return
    total = sum(t[JC.TOPIC_WEIGHT] for t in topic_combinations)
    if total not in (0, 100):
        for t in topic_combinations:
            t[JC.TOPIC_WEIGHT] = round((t[JC.TOPIC_WEIGHT] / total) * 100, 2)


def _parse_evaluation(topic, topic_details, section):
    _require_keys(topic, [JC.ID, JC.NAME])
    topic_id = topic[JC.ID]
    topic_name = topic[JC.NAME]

    if str(topic_id) not in topic_details:
        raise ValueError(f"Falta la definición para el topic id '{topic_id}' en '{JC.TOPICS}'.")

    topic_def = topic_details[str(topic_id)]
    _require_keys(
        topic_def, [JC.EVALUATION_TYPE, JC.TOPIC_VALUES, JC.TOPIC_COUNT, JC.TOPIC_MANDATORY]
    )
    _validate_types(
        topic_def,
        {
            JC.EVALUATION_TYPE: str,
            JC.TOPIC_VALUES: list,
            JC.TOPIC_MANDATORY: list,
            JC.TOPIC_COUNT: int,
        },
    )

    count = topic_def[JC.TOPIC_COUNT]
    _validate_topic_value_lengths(topic_def, topic_id, count)

    topic_weighing_type = _parse_weighing_type(topic_def[JC.EVALUATION_TYPE])
    _normalize_topic_values(topic_weighing_type, topic_def, topic_id)

    evaluation = Evaluation(
        id=topic_id,
        section=section,
        title=topic_name,
        weighing=topic[JC.TOPIC_WEIGHT],
        weighing_system=topic_weighing_type,
    )

    instances = [
        EvaluationInstance(
            evaluation=evaluation,
            index_in_evaluation=i + 1,
            title=f"{topic_name} {i + 1}",
            instance_weighing=topic_def[JC.TOPIC_VALUES][i],
            optional=topic_def[JC.TOPIC_MANDATORY][i],
        )
        for i in range(count)
    ]

    return evaluation, instances



def _validate_teacher_exists(teacher_id):
    if not Teacher.query.filter_by(id=teacher_id).first():
        raise ValueError(f"No existe un profesor con ID '{teacher_id}'.")


def _require_keys(data, keys):
    for key in keys:
        if key not in data:
            raise ValueError(f"Falta la clave '{key}'.")


def _validate_types(data, expected_types):
    for key, t in expected_types.items():
        if not isinstance(data[key], t):
            raise ValueError(f"El campo '{key}' debe ser del tipo {t.__name__}.")


def _validate_topic_value_lengths(topic_def, topic_id, count):
    if len(topic_def[JC.TOPIC_VALUES]) != count:
        raise ValueError(
            f"El tamaño de '{JC.TOPIC_VALUES}' no coincide con "
            f"'{JC.TOPIC_COUNT}' en la definición de topic '{topic_id}'."
        )
    if len(topic_def[JC.TOPIC_MANDATORY]) != count:
        raise ValueError(
            f"El tamaño de '{JC.TOPIC_MANDATORY}' no coincide con "
            f"'{JC.TOPIC_COUNT}' en la definición de topic '{topic_id}'."
        )


def _parse_weighing_type(value):
    try:
        return WeighingType(value.strip().capitalize())
    except ValueError as err:
        valid_types = [w.value for w in WeighingType]
        raise ValueError(
            f"Tipo de evaluación inválido: '{value}'. Los tipos permitidos son: {valid_types}."
        ) from err


def _normalize_topic_values(weighing_type, topic_def, topic_id):
    if weighing_type != WeighingType.PERCENTAGE:
        return

    total = sum(topic_def[JC.TOPIC_VALUES])
    if total not in (0, 100):
        topic_def[JC.TOPIC_VALUES] = [
            round((v / total) * 100, 2) for v in topic_def[JC.TOPIC_VALUES]
        ]
    if round(sum(topic_def[JC.TOPIC_VALUES]), 2) != 100:
        raise ValueError(
            f"La suma de ponderaciones en '{JC.TOPIC_VALUES}' "
            f"debe ser 100 en la definición de topic '{topic_id}'."
        )
