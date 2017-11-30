# edam2json
utility to export EDAM to various sorts of JSON formats (JSON-LD, bio.tools JSON)

# install
pip install git+https://github.com/edamontology/edam2json.git

# run
edam2json ../edamontology/EDAM_dev.owl biotools --root http://edamontology.org/topic_0003 > topic.biotools.json
edam2json ../edamontology/EDAM_dev.owl biotools --root http://edamontology.org/topic_0003 --extended > topic_extended.biotools.json
edam2json ../edamontology/EDAM_dev.owl biotools --root http://edamontology.org/operation_0004 > operation.biotools.json
edam2json ../edamontology/EDAM_dev.owl biotools --root http://edamontology.org/operation_0004 --extended > operation_extended.biotools.json
edam2json ../edamontology/EDAM_dev.owl biotools --root http://edamontology.org/data_0006 > data.biotools.json
edam2json ../edamontology/EDAM_dev.owl biotools --root http://edamontology.org/data_0006 --extended > data_extended.biotools.json
edam2json ../edamontology/EDAM_dev.owl biotools --root http://edamontology.org/format_1915 > format.biotools.json
edam2json ../edamontology/EDAM_dev.owl biotools --root http://edamontology.org/format_1915 --extended > format_extended.biotools.json
edam2json ../edamontology/EDAM_dev.owl biotools --root owl:DeprecatedClass > deprecated.biotools.json 
edam2json ../edamontology/EDAM_dev.owl biotools --root owl:DeprecatedClass  --extended > deprecated_extended.biotools.json

