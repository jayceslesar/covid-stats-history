Sift Papers -> reuse code and improve filters (differentiate queries by keywords)
    dates:
        earliest: literally the first by date
        latest:
    databases: [pubmed, medrxiv preprints, CDC Papers]
    names:     [coronavirus, COVID-19, COVID19, COVID 19, sars-cov-2, sarscov2, sars cov 2, nCov-2019, 2019-nCoV] ! dashes
    paramters: (could all have a range/interval)
        R0           Rate
            -> Infections Period
            -> some papers say R(t) when they mean R0 and swapped
        Transmission Rate (beta of R0)
        !! Testing Rate !!
        !! Mortality Rate !!
        !! Case fatality ratio !!
        !! Asymptomatic Rate !!
        ! undocumented cases -- different than asymptomatic cases
        ! Document complexity
        ! Sample sizes when given (n)
        ! Pie chart of paramater calculation distributions
        ! citations chains -> check dates of refernces
        ! number of times cited -> throw into list and use collections.Counter()
    save:
        text
        date
        where paper was published
        location of study
        (methodology!)

Findings:
    difference in accuracy between publisher
    was there a fanning effect of an R0 in a given location
    how good is a given R0 at a certain time
    were some methodologies better than others?
