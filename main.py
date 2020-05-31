import Article_Sweep
from collections import Counter

def main():
    # weight each param -> word2vec
    manual_params = ['R0',  # high weight
                     'transmission_rate',
                     'testing_rate',
                     'mortality_rate',
                     'case_fatality_ratio',
                     'asymptomatic_rate',
                     'undocumented_cases',
                     'sample_size',  # high weight
                     'methodology',
                     'location_of_interest']

    auto_params = ['title',
                   'abstract',
                   'DOI',
                   'release_date',
                   'publisher',
                   'authored_by']

    good_keywords = ['transmission',
                     'rate',
                     'spread',
                     'infection',
                     'exposed',
                     'mortality']

    bad_keywords = ['Cardio',
                    'gene',
                    'ACE2',
                    'chloroquine',
                    'remdesivir',
                    'favipiravir',
                    'rhinitis',
                    'cytokine',
                    'expression',
                    'PROMOTOR',
                    'capacity',
                    # 'detection',
                    'ecological',
                    'cell',
                    'vaccine',
                    'Antibody',
                    'Structural',
                    'assay',
                    'Genome',
                    'administered',
                    'risk factor',
                    'cross-sectional',
                    # 'diagnosis',
                    'Chest',
                    'Retroviruses',
                    'replication',
                    'dna',
                    'rna',
                    'genetic',
                    'Evolutionary',
                    'psychological',
                    'vulnerability',
                    'genomics',
                    'features',
                    'clinical',
                    'protein',
                    'retrospective',
                    'Pre-existing',
                    'pre existing',
                    'Facebook',
                    'survey',
                    'goggle',
                    'receptor',
                    'proteases',
                    'surveillance',
                    'nucleo',
                    'influenza',
                    'blood',
                    'Antibodies',
                    'antibody',
                    'homology',
                    'Telemedicine',
                    'glyco',
                    'polymerase',
                    'enzyme',
                    'Kidney',
                    'serum',
                    'tool',
                    'strategy',
                    'bat',
                    'Ethics',
                    'inhibition',
                    'surgical',
                    'Working',
                    'flu',
                    'Students',
                    'reflect',
                    'VIRTUAL',
                    'Colleagues',
                    'hydroxychloroquine',
                    'Psychotic',
                    'education',
                    'Tourism',
                    'Effects',
                    'Stress',
                    'Dialysis',
                    'transplantation',
                    'mental',
                    'biologic',
                    'pain',
                    'ophthalmologist',
                    'chronic',
                    'Ventilator',
                    'stroke',
                    'Nucleic',
                    'Molecular',
                    'molecule',
                    'telehealth',
                    'resistance',
                    'NEWS',
                    'drugs',
                    'mobility',
                    'therapeutic',
                    'Commentary',
                    'Guide',
                    'healthcare',
                    # 'Non-Pharmaceutical',
                    'neuro',
                    'brain',
                    'viral',
                    'psych',
                    'governor',
                    'severe',
                    'Return',
                    'Cancer']


    # TODO::implement some sort of smart database
    titles = Article_Sweep.Article_Sweep(good_keywords, bad_keywords, auto_params, manual_params)
    
    
    # words = Counter(titles.words.split()).most_common()
    # problems = [word for word in words if '�' not in word[0] if word[1] > 2]
    # print(problems)

if __name__ == "__main__":
    main()