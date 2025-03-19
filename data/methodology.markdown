# Introduction

An understanding of the costs and benefits involved in developing and
maintaining a proper sanitation system is essential for creating
awareness about the economic impact of sanitation and convincing
authorities to invest in universal coverage. Various studies
were conducted to estimate the costs and benefits of improved water and
sanitation facilities at the global and country levels. However, there
are no city-level studies that would help the policymakers and other
stakeholders understand the benefits of diverting their investment into
improving and expanding sanitation facilities.

The SanOpps Project focuses on tackling this by developing an
innovative tool that will evaluate the costs and benefits that arise out
of investing in sanitation projects in various parts of the
world. SanOpps tool will be user-friendly and hosted in the form
of a website or a mobile application that makes sanitation costs and
return on investments clear and makes nuanced information easy to absorb
through visualizations.

## Objective

This tool aims to help investors at the city level understand the
long-term economic and health benefits that arise from proper sanitation
and encourage them to prioritize sanitation
investments.

## Framework

The user of the tool needs to enter basin information pertaining to the
town. The model projects the population for the next 5 years based on
the demographic data provided. The fifth year becomes the base year. By
this, it is assumed that all the infrastructure will be deployed and the
capital investment will be done. The model calculates the costs and
benefits required for providing access to water, access to sanitation
and cost of training and awareness raising for the projected population
of base year. The life cycle cost analysis is done for 30 years from the
base year.

The development of the model has four parts to it:

-   Costs Calculation

-   Benefits Calculation

-   Life Cycle Costs Assessment

-   Visualizations

This report will discuss the first three stages of the model development
in detail.

# Model

The cost and benefits were calculated in Microsoft Excel which would
later be used for the development of the code and eventually a
dashboard.

## Costs calculation

The cost parameters taken into consideration are broadly divided
    into:

    -   Access to water

    -   Access to toilet

    -   Access to sewered sanitation

    -   Access to non-sewered sanitation

    -   Training and Campaigns

The process of cost calculation and the assumptions made for each
parameter are discussed below.

-   **Access to water:** The cost required to provide Functional
    Household Tap Connections (FHTC)[^1] to every household by the
    target year (2030) is calculated using user inputs for the current
    number of households with piped water supply. It is assumed that
    100% of the projected households will have access to piped water,
    and the cost per FHTC is INR 5,000. Based on the current number of
    households with FHTC and the projected number of households, the
    model will compute the total required cost.

-   **Access to toilets:** Under access to toilets, the focus is given
    to providing toilet facilities to slum and floating populations. The
    figure below illustrates the definition of various sanitation
    facilities.

> ![](images/ct_pt_wc_illustration.png){width="5.547434383202099in"
> height="3.1756692913385827in"}

-   It is assumed that the slum population decrease by 10% in the target
    year due to the National Public Housing Schemes and Slum
    Rehabilitation Program and that the entire projected slum population
    relies on Community Toilets (CT)[^2]. It is also assumed that the
    entire floating population relies on Public Toilets (PT)[^3]. The
    required number of CT and PT are calculated based on the projected
    slum and floating population.

-   The number of people per Water Closet (WC)[^4] is set at 30,
    following the guidelines of Swachh Bharat Mission 2.0. Based on the
    available data on existing toilet blocks, we have assumed an average
    of 20 WCs per community toilet block. Using this assumption, the
    current number of WCs is calculated.

-   The required number of WCs is calculated based on the projected slum
    and floating population and the current number of WCs. The
    construction cost of a WC for CTs is assumed to be INR 98,000. Using
    this and the required number of WCs, the construction costs for CT
    are calculated.

-   It is assumed that the operational and maintenance (O&M) costs of
    CTs and PTs are recovered from the users. O&M cost is usually taken
    care of because PTs have the pay per use model in India. For other
    countries, a percentage factor of capex (1-2%) can be applied.

<!-- -->

-   **Access to sewered sanitation:** It is assumed that the
    *percentage* of the population connected to the sewer network
    remains unchanged between the current year and the target year.
    Using the existing length of the sewer line in the city and the
    population connected to the sewer network, the sewer length per
    person is computed. This is then used to calculate the length of the
    sewer network for the projected population.

    -   The cost of laying the sewer network is assumed to be INR
        4,000,000 per kilometer. With this and the required length of
        the sewer network for the projected population, the capital cost
        for the sewer network is computed. The operational and
        maintenance cost is assumed to be INR 9 per kilometer per year
        which is multiplied by the projected sewer length to obtain the
        total O&M costs.

    -   Cost of sewage treatment is calculated based on the water
        consumption per capita per day and the capacity of the existing
        sewage treatment plants (STPs). It is assumed that 80% of the
        water consumed per person is equivalent to the amount of sewage
        generated per person. Using this and the projected population,
        the total amount of sewage generated and the gap in the
        treatment capacity is calculated. The cost for the treatment is
        assumed to be INR 30,000,000 per MLD (Million liters per day).
        The annual maintenance cost of STP per MLD of wastewater is
        assumed to be INR 800,000.

-   **Access to non-sewered sanitation:** It is assumed that households
    not connected to a sewer network will use septic tanks. Based on
    this, and the projected population change, we calculate the
    projected number of households needing Fecal Sludge and Septage
    Management (FSSM). Septic tanks are expected to be desludged every
    10 years, with 3 kilolitres (KL) of septage emptied per household.

    -   Using the total number of households and the desludging
        frequency, we estimate how many households with septic tanks
        will need desludging in any given year. Assuming 300 working
        days in a year and 3 KL of septage emptied per household, the
        amount of septage to be emptied and treated per day is
        calculated. The daily amount of septage that needs to be emptied
        and treated is calculated.

    -   Following this, to calculate the costs of treatment, the user
        will be asked if there are co-treatment facilities at the
        existing STPs. If the answer is YES, the cost of co-treatment
        will be calculated in the existing or proposed STPs. If the
        answer is NO, the cost of treatment at a fecal sludge treatment
        plant (FSTP) will be computed.

    -   The cost of co-treatment is assumed to be 100,000 INR per KL.
        Using the amount of septage to be treated per day and the cost
        of co-treatment, the total cost of treatment per day is
        calculated.

    -   In case there are no co-treatment facilities and the city is not
        planning to have one, the cost of FSTP will be calculated. Here,
        the user has to provide if there are any existing FSTPs. If yes,
        based on the existing capacity of the FSTPs, the gap in the
        treatment capacity and the cost of treating the same will be
        calculated.

    -   If the answer is no, the cost of treatment of the entire septage
        will be calculated. The septage treatment cost in the FSTPs is
        assumed to be 350,000 INR per KL. Using this the cost of
        treatment of the total septage is calculated. The annual O&M
        costs are assumed to be 50,000 INR per KLD.

-   **Training and Campaigns:** The annual cost of capacity building per
    person is assumed to be INR 10,000. The total number of workers in
    the ULB for the capacity-building programs is assumed to be 0.1% of
    the total population per year. The cost for the same is calculated
    by the model. Meanwhile, the annual cost of the public awareness
    campaign is assumed to be INR 25 per person and is calculated for
    the entire projected population of the city.

## Benefits calculation

-   The benefit parameters taken into consideration are broadly
    classified into

    -   Healthcare costs

    -   Productive time lost (time off work/ time to access water and
        sanitation)

    -   Revenue generated

    -   Value of life

> The process of benefit calculation and the assumptions made for each
> parameter are discussed below.

-   **Healthcare benefits:** This includes savings in medical treatment
    costs and savings in hospital commute costs.

    -   Savings in medical treatment costs are calculated based on the
        number of disease incidences due to diarrhea and other
        water-borne diseases and the unit cost of treatment. The unit
        cost for treatment is assumed to be INR 3000. Based on this, the
        model will calculate the cost savings when the disease
        incidences are averted. The benefit in savings in treatment cost
        per person will be calculated using the total projected
        population.

    -   It is assumed that all the incidences are considered as
        outpatients and that it requires one visit per case. Based on
        the literature, the cost for the commute per visit is assumed to
        be INR 50. The model will compute the total cost savings in
        hospital commute costs and the cost savings per person using the
        number of incidences which will be equal to the number of
        visits.

-   **Productive time lost:** This includes productive time lost due to
    diseases and lack of access to water and sanitation

    -   Based on the literature, it is assumed that the days off work
        per diarrheal incidence is five days. Data on the percentage of
        the population in working age is collected and used as the
        percentage of the working population. Using GDP per capita as
        the proxy for the income, the hourly monetary income is
        calculated (8 work hours per day, 40 work hours per week, and 52
        work weeks per year).

    -   The value of productive time lost for the working age group is
        assumed to be 30% (WHO/HSE/WSH/12.01) of the hourly monetary
        income. Using this the opportunity cost of time for working age
        is calculated. The opportunity cost of time and the number of
        days off of work are used to calculate the productive time
        losses from diseases. The same is calculated for the projected
        population.

    -   For the non-working age group, the same calculation is done
        assuming the productive time lost to be 15% of the hourly
        monetary income (WHO/HSE/WSH/12.01).

    -   The time savings from having access to tap water and access to
        toilets is calculated. For time saved from traveling to collect
        water, it is assumed that a household spends one hour a day
        collecting water from outside sources and the hourly monetary
        income is assumed to be lost due to this. Using the GDP per
        capita as the proxy for monetary income and the number of
        households not having FHTC, the economic benefit of water
        collection time saved is computed by the model.

    -   The time savings from providing access to toilets for slum and
        floating populations is estimated at 0.5 hours per day, with 30%
        of the hourly income assumed to be lost due to the lack of
        access. Using GDP per capita as a proxy for income, the economic
        loss is then calculated.

-   **Revenue generated:** This includes revenue generated from
    the reuse of treated wastewater and an increase in tourism due to
    improved sanitation.

    -   In the case of the reuse of treated wastewater, it is assumed
        that 20% of the wastewater generated is reused, based on
        government policy in India, which mandates utilizing at least
        20% of treated wastewater for reuse. It is also assumed that the
        price of treated wastewater is 15 INR/KL or m^3^. The price of
        treated wastewater for non-potable uses in India ranges from
        12-19 INR per INR was taken as an average value. Based on this,
        the annual benefit arising out of reusing treated wastewater is
        calculated.

    -   The price of treated wastewater varies based on its quality. For
        high-quality treated wastewater, the cost typically ranges from
        25 to 30 INR per KL. Additional treatment costs should be
        considered for this. However, as we are assuming we are reusing
        the water for non-potable purposes, additional treatment are not
        necessary.

    -   It is well known that improved sanitation practices bring in
        more tourists. Literature shows the loss in GDP ranges from
        5-15%[^5] due to poor sanitation in various countries, for
        example 6% GDP loss in India in 2006. We have assumed 10% could
        be the increase with reference to these articles, but this value
        could be adjusted with further expert review or new literature
        sources. In 2023, tourism contributed to 9.1% of India's GDP.
        Using this, the per capita GDP contribution is calculated which
        is then used to calculate the increase in GDP per capita.

-   **Value of life:** The value of life is calculated using the human
    capital approach. We are assuming the number of years lost for the
    working and non-working age groups as 19 years and 22 years
    respectively based on the literature. Using this and the GDP per
    capita as the proxy for the income lost, the economic value of lives
    lost is computed by the model.

## Life cycle cost assessment

Sanitation infrastructure, including sewer networks and sewage treatment
plants, typically has a lifespan of 30 to 40 years. To fully understand
the total investment, operational, and maintenance costs over this
period, a Life Cycle Cost Assessment (LCCA) is performed. In our case,
we assume that the infrastructure will last for 30 years from the base
year. Below are the key components of the cost and benefit analysis:

### Cost components

-   **Capital Expenditure (CapEx):** This includes the one-time costs
    associated with planning, supervision, hardware, and construction.
    For this analysis, it is assumed that all capital expenditures are
    incurred by the base year.

-   **Operational & maintenance Expenditure (OpEx):** These are
    recurring costs required for the regular operation of the
    infrastructure, including labor, energy, chemicals, and other
    ongoing expenses. It is assumed that operational costs will be
    recovered from users through tariffs or service charges.

### Benefit components

-   The benefits are expected to begin from the base year and are
    calculated on an annual basis.

### Final assumptions

-   An inflation rate of 4% and a discount rate of 6% are assumed for
    this analysis. Costs and benefits are projected annually, and the
    Benefit-Cost Ratio (BCR) is calculated for every decade.

-   To account for the time value of money, the compounded costs and
    benefits are discounted to their Net Present Value (NPV) using the
    6% discount rate. This discounted NPV is then used to determine the
    final BCR.

[^1]: Functional Household Tap Connection - A tap connection to a
    household for providing drinking water in adequate quantity of
    prescribed quality on a regular basis (Jal Jeevan Mission, India)

[^2]: Community Toilet (CT) - Toilet facilities that are shared by a
    group of households within a community, especially in areas where
    individual household toilets are not feasible (Joint Monitoring
    Program)

[^3]: Public Toilet (PT) - Public toilets are sanitation facilities that
    are open for public use and not limited to specific households or
    groups (Joint Monitoring Program)

[^4]: Water Closet (WC) - Refers to a single toilet that is flushed with
    water and is usually connected to a sewer system or a septic tank.

[^5]: ​​<https://documents1.worldbank.org/curated/en/820131468041640929/pdf/681590WSP0Box30UBLIC00WSP0esi0india.pdf>

[^6]: <https://www.unicef.org/india/media/1221/file/Potential-Impact-of-Sanitation.pdf>

[^7]: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1149071>

## Septage Treatment Decision Matrix

The following table outlines the cost implications based on the availability of co-treatment facilities at Sewage Treatment Plants (STPs) and Fecal Sludge Treatment Plants (FSTPs):

| Is CO treatment facility available at the existing STP? | Is the town proposing CO treatment at STP? | Does the town have FSTP(s)? | Capital Cost | Maintenance Cost |
|--------------------------------------------------------|-------------------------------------------|----------------------------|--------------|------------------|
| Yes | Yes | - | 0 | 0 |
| No | Yes | - | Cost of CO treatment | 0 |
| No | No | Yes | Cost of setting up of FSTP | Additional Septage ✕ INR Per KLD |
| No | No | No | Cost of setting up of FSTP | Additional Septage ✕ INR Per KLD |
