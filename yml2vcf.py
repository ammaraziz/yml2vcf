#!/usr/bin/env python3
import yaml
import vcf
import argparse


def register_arguments():
    parser = argparse.ArgumentParser(
        description="convert yaml to vcf",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--input", required=True,
                        help="Input yaml file")
    parser.add_argument("-o", "--output", required=True,
                        help="Output vcf file")
    args = parser.parse_args()
    return(args)


def flatten(d):
    out = {}
    for key, val in d.items():
        if isinstance(val, dict):
            val = [val]
        if isinstance(val, list):
            for subdict in val:
                deeper = flatten(subdict).items()
                out.update({key + '_' + key2: val2 for key2, val2 in deeper})
        else:
            out[key] = val
    return out


def create_header(yaml):
    '''
    the rest    :   data parsed from yaml file, usually a dictionary
    call_def    :   use flatten function first
    '''
    try:
        call_definitions = ','.join('{}:{}'.format(key, val)
                                    for key, val in flatten(yaml['calling-definition']).items())
    except AttributeError:
        call_definitions = '.'

    try:
        acknowledgements = str(yaml['acknowledgements'])
    except KeyError:
        acknowledgements = "."
    header = [
        '##fileformat=VCFv4',
        '##INFO=<ID=EFF,Number=.,Type=String,Description="Variant effects are encoded in the ANN field: ANN=A|...., T|.... Annotation fields follow order of yaml file separated by pipe symbol \">',
        '##META=phe-label:' + yaml['phe-label'],
        '##META=alternate-names:' + yaml['alternate-names'][0],
        '##META=belongs-to-lineage:' + str(yaml['belongs-to-lineage'][0]),
        '##META=description:' + yaml['description'],
        '##META=info_source:' + str(yaml['information-sources'][0]),
        '##META=calling-definition:' + call_definitions,
        '##META=acknowledgements:' + acknowledgements,
        '##META=curators:' + ', '.join(yaml['curators']),
        '# CHROM POS ID REF ALT QUAL FILTER FORMAT INFO'
    ]

    return(header)


def create_record(yaml_variant):

    try:
        effect = yaml_variant['predicted-effect']
    except KeyError:
        effect = '.'

    try:
        aa_pos = yaml_variant['protein-codon-position']
    except:
        aa_pos = '.'

    try:
        codon_change = yaml_variant['codon-change']
    except:
        codon_change = '.'

    annotation = '{variant_base}|Gene:{gene}|{effect}|{type}|{protein}|{aa_pos}|{codon_change}'.format(
        variant_base=yaml_variant['variant-base'],
        gene=yaml_variant['gene'],
        effect=effect,
        type=yaml_variant['type'],
        protein=yaml_variant['protein'],
        aa_pos=aa_pos,
        codon_change=codon_change
    )
    record = {
        'CHROM': '1',
        'POS': yaml_variant['one-based-reference-position'],
        'ID': '.',
        'REF': yaml_variant['reference-base'],
        'ALT': yaml_variant['variant-base'],
        'QUAL': '.',
        'FILTER': '.',
        'FORMAT': '.',
        'INFO': 'ANN|{ann}'.format(ann=annotation),
    }
    return(record)


def write_vcf(yaml, output_file):

    vcf_header = create_header(yaml)
    vcf_body = []

    for var in input_yaml['variants']:
        record = create_record(var)
        vcf_body.append('\t'.join(str(x) for x in record.values()))

    with open(output_file, "w") as outfile:
        for line in vcf_header:
            outfile.write(line + '\n')
        for line in vcf_body:
            outfile.write(line + '\n')


if __name__ == "__main__":

    args = register_arguments()

    with open(args.input, "r") as stream:
        input_yaml = yaml.safe_load(stream)

    write_vcf(input_yaml, args.output)
# writing out vcf
# for the vcf header
