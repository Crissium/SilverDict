from .michaelis import transform_michaelis
from .oxford_hachette import transform_oxford_hachette
from .harrap import transform_harrap

transform = {
	'por-eng_michmoddic_an_1_1': transform_michaelis,
	'eng-por_michmoddic_an_1_1': transform_michaelis,
	'eng-fra_hachette-oxford_le_1_3': transform_oxford_hachette,
	'fra-eng_hachett-oxford_le_1_2': transform_oxford_hachette,
	'eng-fra_harraps_unabridged_le_1_0': transform_harrap,
}
