# greener

Greener is a data visualization tool that lets users see the relationship between different factors based on county level data in an effort to provide users with actionable information when looking to make a move. Users can select the criteria they wish to view, and either pan around the map, selecting counties based on their shading, or select from the top ten counties shown in the bar graph beneath the map.

## How are counties scored?

Counties are scored with log10 and min-max scaling and as ratios. Applying the scaling results in a score from 0 to 1 for each variable of each county. Scores are summed based on the criteria selected by the user, and those sums are used to rank and map the counties.

### Log10 Scaling

Log-10 scaling is the practice of converting each datapoint to is log10 value. Doing this addresses the skewnewss of the data. For example, prior to applying log10 scaling to the home value data, a handfull of counties with average home values in the millions created a skewed dataset, where home prices from $100,000 to $500,000 were effectively the same spot on the scale. Using log10 scaling means that while high values are still represented at the top of the scale, there is greater variation between lower values, where most of the data resides.

Data that was scaled with log10 scaling: Average Home Values

### Min-Max Scaling

Min max scaling is the practice of scaling numerical values down to fit within a specified range, in this case 0-1. The lowest number in the dataset will be given a value of 0, and the highest a value of 1. The remaining numbers are placed on the spectrum between 0 and 1. This process makes it easier to compare values of different scales. For example, the average home value of a county could realistically be $1,000,000, but it is unlikely that a counties median annual income would be that high. Instead, $100,000 is a more realistic number. Because of this variation, if we compared a county with $1,000,000 homes and $200,000 incomes to one with with $500,000 homes and $100,000 incomes, the county with the higher incomes would likely score worse due to the large nominal difference in home prices, when clearly they are proportial to the income prices. The very high home value is skewing the results. In order to compare incomes and home values across counties, we need to scale the values so that a county with very high median income (e.g. $100,000) and a county with a very average high home value (e.g. $1,000,000) both carry the same weight.

Data that was scored via min-max scaling: Average Home Values, Median Household Income, Average Temperatures, Unemployment Rate, Population

### Ratios

Ratios are the direct relationships between two numbers. For example, a county with 50,000 Democratic votes and 100,000 Republican votes has a Democratic to Republican ratio of 1:2, or .5. Ratio scoring was chosen for data that contains two diametrically opposed variables. This is a simple way to score the variables when the relationship between those two variables is more important than the variables themselves.

Data that was scored via ratio: Political Affiliation

## About the Data

### Median Annual Home Values

Source: [Zillow]("https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv?t=1750261630")

Zillow publishes monthly reports on the average home sales prices in each county in the United States. From this data I extract the most recent month's average price, scale those prices with log10, and then score them from 0-1, with 0 being the highest prices and 1 being the lowest. This inverse min-max scaling is used with the assumption that lower home prices are better when deciding where to live. 
