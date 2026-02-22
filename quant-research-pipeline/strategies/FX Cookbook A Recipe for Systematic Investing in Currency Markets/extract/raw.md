Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
Deutsche Bank
Research

Global
Quantitative Strategy
Quantcraft
Date
15 January 2019

Vivek Anand
vivek-v.anand@db.com

FX Cookbook: A Recipe for Systematic
Investing in Currency Markets

This is the twentieth edition of our Quantcraft series. This periodical outlines
new trading and analytical models across different asset classes.

Foreign exchange is present in most institutional portfolios and corporate
balance sheets. That said, it often receives less attention than deserved,
therefore often being a source of risk but not a source of reward. This
Quantcraft aims to change that.

This report introduces a "cookbook" for systematic investing in the asset
class, with recipes of short, medium and long-term signals. Importantly, we
also describe a broad framework for strategy selection, implementation and
rebalancing. Issues such as market neutrality versus directionality, signal
smoothing and filtering, and portfolio tranching are carefully addressed.

We describe 4 short-term signals: Momentum Spill-Over from the interest rate
market, DTCC positioning (COFFEE), CFTC Momentum and CFTC Reversal.

We also describe 2 medium-term signals and 1 long-term signal: Momentum
and Carry, and Value.

We describe optimal implementation for absolute return portfolios and for
currency hedging, thereby covering a broad scope of currency market
participants.

> Figure 1: FX Cookbook
[Figure: A flat lay image showing various ingredients and a hand holding an open cookbook, symbolizing the "FX Cookbook" theme.]

Caio Natividade
caio.natividade@db.com

George Saravelos
george.saravelos@db.com

Jose Gonzalez
jose.gonzalez@db.com

Shreyas Gopal
shreyas.gopal@db.com

Rohini Grover
rohini.grover@db.com

North America: +1 212 250 8983
Europe: +44 20 754 71684
Asia: +852 2203 6990

Deutsche Bank AG/London
Distributed on: 15/01/2019 10:00:27 GMT
Note to U.S. investors: US regulators have not approved most foreign listed stock index futures and options for US
investors. Eligible investors may be able to get exposure through over-the-counter products. Deutsche Bank does and
seeks to do business with companies covered in its research reports. Thus, investors should be aware that the firm may
have a conflict of interest that could affect the objectivity of this report. Investors should consider this report as only a
single factor in making their investment decision. DISCLOSURES AND ANALYST CERTIFICATIONS ARE LOCATED IN
APPENDIX 1.MCI (P) 091/04/2018.

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

# FX Cookbook: A Recipe for Systematic
# Investing in Currency Markets

# 1. Introduction

Foreign exchange is present in most institutional
portfolios and corporate balance sheets. That said, it
often receives less attention than deserved, therefore
often becoming a source of risk but not reward. Earlier
in May we showed that the presence of non-profit
seeking participants provides scope for harnessing
value from currency markets. This “cookbook" provides
some suggestions on how to do so systematically.

Section 2 uses econometrics to describe the drivers of
contemporaneous and future market returns, as well as
the interactions between them across multiple horizons.
Section 3 introduces a framework for estimating
predictive power in a more dynamic, signal-specific
format that guides us on major implementation aspects.
Section 4 describes how we build signals from each
driver and implement them in absolute return portfolios.
In total, we introduce 7 signals that cover short, medium
and long term horizons. Section 5 applies a subset of
these signals for currency risk management, where we
introduce 4 informed dynamic currency hedging
methods. Section 6 concludes.

## 1.1 Our dataset

Unless stated otherwise, we utilize 1-month forwards in
24 USD/FX¹. Positions are executed at the NY close, 1
business day after they have been calculated (t+1). Thus
if a target portfolio is calculated at the end of Tuesday
October 2nd, 2018, the respective trades are only
executed at the close on Wednesday October 3rd, 2018.
We apply fixed bid-ask spreads, estimated as the long-

term historical average multiplied by 1.5x, as our
transaction cost estimate.

## 1.2 Risk estimation

We estimate risk – volatilities, correlations and betas –
primarily through covariance matrices of historical
currency returns.²

These are built using the classical (historical sample)
method but with an exponential decay parameter. We
seek a balance between robustness and adaptivity when
choosing parameter values; off-diagonal elements
utilise a 3-year decay while the elements of our main
diagonal use a 1-year decay. This is in line with the view
that volatility estimates should be highly adaptive, while
correlation estimates should be stable.

Finally, unless otherwise stated, we use 3-day non-
overlapping asset returns³, as opposed to daily returns,
so as to reduce noise and timezone differences.

# 2. Identifying the Investment Factors

Our first task is to identify the most important factors
explaining foreign exchange returns; in other words, the
drivers of the asset class. We focus on explaining
returns over short, medium and long-term frequencies
using all our historical data. This allows us to get a better
feel for factor persistence.

We apply two tools: principal component analysis and
panel regressions. The first focuses on explaining
contemporaneous returns, while the second evaluates
which factors are better return predictors.

1 USD vs AUD, EUR, GBP, CHF, SEK, NOK, NZD, CAD, JPY, BRL, CZK,
KRW, MXN, PLN, RUB, SGD, TRY, TWD, ZAR, CZK, HUF, ILS, INR and
THB.
2 We use historical, as opposed to implied currency returns. While
currency markets are unique in providing implied correlation data between
currency pairs, thus allowing us to compute a market-implied covariance
matrix, we opted against that approach due to data limitations - especially
with regards to implied correlations between reference asset portfolios (or
the PC1 of the asset class) and each currency pair. The risk that using
options market data would yield an over-conservative risk estimate also
played a role in our final choice, given the bias in implied volatilities and
correlations when predicting their future empirical statistics. Risk
estimation is a key part of our work, as seen in Ward et al (2016),
Natividade and Brehon (2009) and Natividade et al (2017), and new
methodologies will be considered for implementation in this context
should they look promising.
3 Specifically, we estimate 3 separate matrices of 3-day non-overlapping
returns. Each starts one day after the other. The final covariance matrix is
the average of the 3.

Page 2
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

## 2.1 Principal Component Analysis (PCA)

Following the standard recipe found in quant cookbooks,
we first apply PCA to better understand the common
variations of currency market returns. This is a useful
tool in that it "distills" large data pools into a smaller set
that represents the main variations of the whole dataset.

We ran this exercise on a slightly larger set of 27
currencies; it may still look small for the cross-asset
investor, but FX is unique in that it can imply a lot more
than just 27 time series. Currencies are traded in pairs,
and therefore there are potentially 351 return streams⁴
to be analysed. Each stream - say, EUR/JPY for instance
reflects the driving forces of both currencies (the EUR
and the JPY in this case). Therefore, in order to isolate
the returns attributed to each separate currency, one
must consider baskets of pairs with that currency in
common so as to better understand its own specific
drivers.

As such, we built 27 separate baskets, each formed
using pairs with one common base currency, and
applied PCA on each of those. This particular multi-
basket PCA exercise was conducted on daily returns and
revealed significant correlations between each USD/FX
rate and each of the respective PC1s - which explain, on
average, 52% of the variations in each basket a high
number in the context of other asset classes⁵. In other
words, most returns in each currency group - for
instance, the ZAR/FX basket - are already captured in the
USD exchange rate - in this case, USD/ZAR.

This should not come as a surprise as the USD crosses
are often the most liquid⁶, and hence the first port of call
for incorporating new market information. Figure 2
shows these correlations in more detail.

This finding allowed us to condense the number of
inputs going into our multi-currency, multi-frequency,
multi-start date study. Instead of 27 individual baskets,
the remaining steps of this study focused therefore on
USD/FX returns alone.

The next step was to apply PCA to a USD/FX basket,
accounting for multiple frequencies as we are interested
in multiple horizons. As some of the horizons are long-

term, we also applied re-sampling in order to reduce
discretization error.⁷

> Figure 2: Long-term correlation of daily returns between
> base currency PC1 and CCY/$ pair

| $/FX | PC1 |
| :--- | :--- |
| USD | 0.70 |
| EUR | -0.74 |
| JPY | -0.67 |
| CHF | -0.72 |
| GBP | -0.66 |
| AUD | -0.86 |
| NZD | -0.83 |
| CAD | -0.67 |
| NOK | -0.80 |
| SEK | -0.80 |
| PLN | -0.94 |
| MXN | -0.83 |
| BRL | -0.92 |
| TRY | -0.90 |
| ZAR | -0.29 |
| SGD | -0.26 |
| TWD | -0.27 |
| KRW | -0.79 |
| THB | -0.24 |
| INR | -0.47 |
| MYR | -0.46 |
| IDR | -0.79 |
| ILS | -0.53 |
| CZK | -0.91 |
| HUF | -0.95 |
| RON | -0.87 |
| RUB | -0.87 |

Data since 1971 or as per Section 1. The correlations are broadly negative as we assessed FX/$ as
opposed to $/FX. Source: Deutsche Bank

The results of our multi-frequency PCA exercise point to
the following:

*   The first principal component is dominant across
    return frequencies, explaining an average of 54% of
    the total return variation as shown in Figure 3. It has
    a positive and stable loading onto each asset, as is

4 That is, all possible pairwise combinations of 27 currencies (27*26/2).
5 For completeness, we also ran the exercise on the full combination of
base and quote currencies in G-10 (45). The first principal component
explained circa 30% of the variations across horizons below 2 years, and
the loading of each currency pair related to its interest rate differential. The
second principal component, which explained circa 25% of the variations
across horizons, correlated more strongly to the US dollar despite much of
the direct USD effect being cancelled out by the inclusion of all other cross
exchange rate variations.
6 For context, the share of common variations in equity indices is circa
45%, 30% in bond futures, 25% in commodity futures, and 33% in US
corporate credit CDS. See Natividade et al (2013) and Gonzalez et al (2018)
for details.
7 A few European currencies are the exception, where most liquidity is in
the EUR/FX cross. But even there, the volatility in EUR/FX is typically
lower; PC1 correlates highly with the USD/FX pair as it also picks up
EUR/USD volatility.
8 Discretization error in the sense that using different start dates could
produce different results. In our re-sampling, we repeated the PCA
multiple times, using all available unique start dates. We used, for
instance, 4 start dates to analyse weekly returns and 249 start dates to
analyse annual returns, generating 4 and 249 separate PCAs outputs, of
which we calculated the average. This allowed us to reduce any bias
associated with the exact dates that market data was snapped.

Page 3
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

typical when delineating the market factor of an asset
class. In this context, we interpret PC1 as
representing the US dollar factor.

> Figure 3: Explanatory power by principal
> component for various horizons (USD/FX basket)
[Figure: A line chart showing the explanatory power of PC1, PC2, PC3, and PC4 across different business day horizons, with PC1 being dominant.]

Source: Deutsche Bank

> Figure 4: PC1 loading (USD/FX baskets) according to
> horizons and classification
[Figure: A line chart showing PC1 loadings for various currency baskets (high yield, medium yield, low yield, developed markets, emerging markets, etc.) across different business day horizons.]

Currency baskets: HY: high yield, MY: medium yield, LY: low yield, DM: developed markets, EM:
emerging markets, EM HY: EM high yield, EM LY: EM low yield, G10 HY: developed high yield, X:
exporters, M: importers, N: neutral, LA: Latin America, EU: Europe, EMEA: Europe, Middle East and
Africa, A: Asia. Source: Deutsche Bank

*   The second principal component explains an
    additional 13% of the variations in returns across
    frequencies. The sign and intensity of how it loads
    onto each currency relates strongly to the interest
    rate differential between the USD and that currency.
    This strongly indicates a link between PC2 and the
    carry trade, and hence we interpret it as the carry
    factor.

*   The sign of the PC2 loadings inverts as we move from
    short to long-term frequencies. Figure 5 plots the
    cross-sectional beta of interest rate differentials to
    PC2 loadings. Importantly, as shown in Figure 6, the
    beta flips from heavily positive in frequencies under
    9 months to notably negative in frequencies beyond

5 years. This negative relationship between loadings
and frequencies - and therefore short-term PC2 and
long-term PC2 - is concomitant to the argument that
covered interest rate parity is more likely to hold in
the long run than in the short term. To the extent that
high interest rate countries also witness high
inflation, this finding suggests that high inflation
countries should see their currencies depreciate in the
long run - a standard claim from traditional currency
valuation models.

*   The way that higher order principal components load
    onto each currency pair is unstable as we change the
    return frequencies. This suggests that PC3 and above
    are more likely to be picking up noise. Figure 7 shows
    examples for PC3 and PC4.

> Figure 5: PC2 loading versus interest rate differentials
> (1M and 10Y returns)
[Figure: Two scatter plots showing PC2 loading against Carry vs USD, for 1M returns and 10Y returns, with R-squared values.]

Note: both X and Y values have been cross-sectionally standardized. Source: Deutsche Bank

These results suggest that the two key factors of interest
are the US dollar and carry; they are the two broad
drivers of the foreign exchange asset class.

This statement should not surprise the reader. Verdelhan
(2012, 2018) also outlines the influence of both US dollar
and carry as key determinants of exchange rate

Page 4
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

variations, although the former is formulated differently⁹.
The two factors are also often used as control variables
when authors look to introduce new currency drivers.
Finally, it also concurs with prior DB research - see, for
instance, Giacomelli and Zhang (2016) and Natividade et
al. (2013).

> Figure 6: Sensitivity of PC2 loadings to interest rate
> differentials versus the USD according to return
> frequency
[Figure: A line chart showing the cross-sectional beta of PC2 loading onto carry across different return frequencies (1d to 10y).]

Note: both X and Y values have been cross-sectionally standardized. Source: Deutsche Bank

> Figure 7: Average PC3 loading of currency groups
> according to return frequency
[Figure: A line chart showing average PC3 loading for various currency baskets across different business day horizons.]

Currency baskets: HY: high yield, MY: medium yield, LY: low yield, DM: developed markets, EM:
emerging markets, EM HY: EM high yield, EM LY: EM low yield, G10 HY: developed high yield, X:
exporters, M: importers, N: neutral, LA: Latin America, EU: Europe, EMEA: Europe, Middle East and
Africa, A: Asia. Source: Deutsche Bank

That the direction of the dollar is the most important
driver of the currency market is widely agreed upon, but
not enough. A proper understanding of the asset class
requires understanding the fundamental forces behind
the US dollar itself, and that is far harder. Broadly

speaking, drivers can be broken down into short-term,
medium-term and long-term factors. Short-term factors
would tend to be dominated by positioning, speculative
sentiment, market microstructure and idiosyncratic FX
flows. Medium-term factors include the monetary and
fiscal policy outlook, relative growth rates, terms of
trade shocks, current accounts, and capital flow trends.
Long-term factors include shifts in purchasing power
parity, productivity trends and changes to saving-
investment imbalances.

This rich pool of variables notwithstanding, the
academic literature has had little success in building a
coherent modelling approach to exchange rates that
outperforms the random walk in what has come to be
known as the “exchange rate determination puzzle”¹⁰.

Our favoured interpretation of this result¹¹ is that the FX
market and "dollar trend" suffers from high levels of
complexity that make the application of a unified
modelling technique particularly difficult. The closest
equivalent to this observation in the physical world
would be what are known as "complex systems" such
as the global climate or human brain. These systems,
similar to FX, are characterized by non-linearities,
feedback loops and a high-sensitivity to initial conditions
that makes the application of a unified modelling
approach particularly challenging.

More importantly, the presence of a dynamic system
does not preclude FX from being a profitable asset class.
As we have demonstrated elsewhere¹² and this paper
will expand upon there is strong evidence on the
presence of excess returns in FX over time. Importantly,
however, we must also ensure that our modelling
approach is flexible and inclusive.

## 2.2 Panel Regressions

Having explained the main variations through statistical
factors, we now seek to apply factor analysis to predict
future FX returns. For that, we apply panel regressions.
This approach not only allows us to introduce future FX
returns as dependent variables, but also add peripheral,
tangible factors to the mix. Addressing multi-collinearity
is key, as the causality effects often work both ways.

In choosing our explanatory variables we opted for a
combination of fundamental and market data, as
dictated by the academic literature. After careful
scrutiny, we opted for a small set of representative
variables as opposed to the wide, "kitchen sink"
approach.¹³ The candidates we opted for are:

9 Verdelhan (2015, 2018) uses the term slope factor to characterise the
same US dollar factor; the author formulates it as the cross-section of
dollar beta-sorted currency returns.
10 See Cheung et al (2002).
11 Another interpretation is that the USD trend itself is truly random.
12 See Saravelos et al (2018).
13 Our choice is somewhat in line with recent efforts in both academia and
industry to apply greater scrutiny when choosing investment factors. A
good example of that is in Harvey and Liu (2018), where the authors
advocate using bootstrap-based re-sampling as a way to decide which

Page 5
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

(1) The market factor, represented by the first principal
    component of a USD/FX basket.¹⁴

(2) A sentiment factor, represented by a basket of
    USD/FX implied volatilities.¹⁵

(3) Dummy variables representing regional and trade
    balance characteristics.¹⁶

(4) A price action factor, calculated on currency returns
    orthogonal to the market factor.¹⁷ The lookback
    window for cumulative returns is the same as our
    regression frequency.

(5) A long-term price action factor, calculated on 5-year
    currency returns orthogonalised against the market
    factor.¹⁸

(6) A carry factor, calculated according to the
    percentage distance between the 6-month USD/FX
    forward and spot.¹⁹

(7) A monetary policy factor, calculated as the change in
    nominal 6-month interest rates over a period equal
    to our regression frequency.²⁰

(8) The long-term forward, as a potential measure of
    currency valuation.²¹

(9) Purchasing power parity (PPP), as estimated by the
    BIS, as another measure of currency valuation.²²

(10) A macroeconomic growth factor, proxied by our
    DB Nowcast Beat indicators for country growth.²³

Having decided on the explanatory variables, the next
step was to define the regression format. We opted for
panel regressions as they capture both the time series
and cross-sectional aspects of the asset class without
suffering from data shortage. We also opted against the
Fama-McBeth²⁴ approach as not only we lacked cross-
sectional breadth, but we were not as interested in
evaluating how the investor is compensated from
exposure to any particular driver; such is addressed
separately in Sections 3 and 4.

We evaluated multiple horizons of future returns,
ranging from daily to 9 months.²⁵ For a given frequency,
the regression steps were as follows:

1. We set future USD/FX returns (from current to next
    evaluation date) as the dependent variable, and the
    current value of each of the 10 explanatory variables
    above as independent variables.

factors to include. We opted for a simpler method - stepwise regressions -
as the number of candidate regressors is already small.
14 Using a "market factor" is common practice in the finance literature,
given the use of CAPM-type models in investment research. We proxied it
by using the PC1 of a basket of global USD/FX pairs, rolled monthly, where
the covariance matrix is built using 1 year of rolling daily returns and
assumes unit variance. We calculate the 5-year rolling time series
sensitivity of each USD/FX pair to this PC1, and the corresponding beta
becomes the market factor for each currency pair - i.e. the market "score".
15 We proxy "sentiment" through a time series that collates 3-month
realised volatility of the USD/FX PC1 described above from Sep-80 to Jan-
91, and the 3-month DB Currency VIX (CVIX3I Index on Bloomberg) from
Jan-91 onwards. We opted not to add other option market variables given
their strong link to the CVIX itself, as per Natividade et al. (2015). Therefore
we believe this variable also encompasses the volatility factor in Menkhoff
et al. (2010) and Christiansen et al. (2010)), the global factor in Lustig et al.
(2011), the skewness factor in Rafferty (2012), and the correlation factor in
Mueller et al. (2013). We also note that some of these factors were
constructed in order to explain the returns of FX Carry portfolios, as
opposed to currency returns. The sentiment "score" for each asset is
estimated in the same way as the market score.
16 The dummy variables characterise currencies according to region (G-10,
Asia, EMEA, EU and LatAm) and trade (exporters and importers). It partly
follows the approach used in Giacomelli and Zhang (2016). We omit one of
the descriptors (EM FX) in order to remove perfect collinearity. For clarity,
the import currencies are: EUR, INR, JPY, KRW; the export currencies are:
AUD, NZD, BRL, CAD, CLP, COP, MYR, NOK, PHP, RUB, ZAR.
17 This is, in essence, a measure of residual momentum (or residual
reversal) and is in line with the equity market literature (Gutierrez and
Pirinsky (2007), Kasssam et al (2010), Blitz et al (2011) and Chaves (2012)),
and credit market literature (Jostova et al. (2013) and Haesen et al. (2017)).
It also helps reduce the collinearity between the market and price action
factors. We believe this partly covers the momentum factor in Gutierrez
and Kelley (2008), Burnside et al. (2011), Menkhoff et al. (2011) and Raza et
al. (2013).
18 We use it as a simple version for currency valuation, as it is based on
the premise of long-term reversion in currency returns. This is partly based
on Engel and Hamilton (1990).
19 The FX carry factor has been widely mentioned in the academic
literature, most recently under the label of slope factor in Lustig et al

(2011) and Verdelhan (2015, 2018) due to a slight difference in
construction. We opt for using 6-month implied yields due to the
smoothness and historical length.
20 Currency analysts often use relative interest rate changes as input to
their short-term views - see, for instance, Rosenberg (2002). Yield curve
determinants have been more generally addressed in Chen et al. (2009),
Ang et al. (2010), Georges et al. (2014), Natividade et al. (2014) and
Natividade et al. (2015).
21 It is a (simple) version for currency valuation if one considers the
premise that interest rate parity holds over long horizons.
22 Purchasing Power Parity models have been used to explain long-term
reversion in currency values, with Rogoff (1996) and Neely (1998) serving
as good reference. As such, we use it as a potential explanatory factor of
currency returns. They are also often used as input to currency valuation
strategies, with Hafeez (2007), Serban (2010) and Asness et al. (2013)
serving as recent examples. We used BIS USD PPP values prior to 1994,
and BIS REER values (translated into USD PPP via matrix inversion) post
1994. We lagged the data by 2 months so as to remove the time lag
between applicable date and reporting date. We avoided using other
estimates of valuation - such as BEER, FEER and DBEER - as we did not
have enough history for those.
23 The DB Nowcast Beat indicators, introduced in Natividade et al. (2014),
extract the first principal component of a basket of both hard and soft
growth data in 26 countries and regions. Examples include retail sales,
industrial production, unemployment, trade and GDP growth as hard data,
and consumer sentiment and business sentiment as soft data. Albeit
unsuccessful in our use of the Beat indicators for building single currency
strategies, we added them to this analysis given how they proxy - well or
poorly - other potential explanatory variables shown in the literature.
Examples of the latter include: the consumption growth factor in Lustig
and Verdelhan (2007, 2011), the surplus-consumption risk factor in
Riddiough (2014), the size factor in Hassan (2013), and the economic
momentum factor in Dahlquist and Hasseltoft (2016). We also note that
some literature points to currencies driving future macroeconomic
performance, and not the other way around; see, for instance, Engel and
West (2005) and Sarno and Schmeling (2013).
24 Fama and MacBeth (1973).
25 We removed longer horizons due to the significant shrinkage of time
series breadth in the data.

Page 6
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

2. We apply cross-sectional standardisation in both the
    dependent and independent variables, thereby
    reducing the effect of outliers. We apply an inverse
    z-score standardisation method as described in
    Natividade et al. (2014).

3. We apply a stepwise regression algorithm to address
    multicollinearity between explanatory variables.²⁶
    This step narrows the number of potential
    explanatory variables to a much smaller set.

4. We re-run the stepwise regressions, but now using
    only the qualifying explanatory variables from Step
    (3). The procedure is different in that we now run a
    sequence of univariate stepwise regressions,
    evaluating the marginal contribution of each
    regressor in explaining the residual returns from the
    previous univariate regression. We tested all
    available sequences, and calculated the average
    results. This extra step allowed us to better estimate
    the influence of each individual regressor.

As was the case with the PCA study, our panel
regressions were repeated with different start dates so
as to reduce the noise coming from data discretization.
The final results use an average of all regressions.

> Figure 8: Marginal explanatory power from panel
> regressions according to independent variable and
> forecast horizon (days)
[Figure: A stacked bar chart showing the marginal explanatory power of different independent variables (Idiosyncratic Betas, Carry, MonPol, Region, LT Fwd, P.Action, PPP, Growth) across various forecast horizons.]

Source: Deutsche Bank

These results both confirm and contradict those from
Section 2.1. First, they confirm the relevance of the carry
factor; in addition to being a key factor explaining the
current variations of the asset class, it is also the top
predictor of future returns.

On the other hand, these results are also discouraging
on the US dollar. It may be the biggest factor explaining
contemporaneous returns, but it fails to explain much of
the future variations in the asset class. This lends further
support to our previous allusion to complex systems,
where different factors are intertwined. The USD factor
is often entangled with alternative drivers such as
valuations, monetary policy and market sentiment,
which are also as our regressions show - clear drivers
of the US dollar as well.

By adding clarity on other factors, which were not
immediately clear from the PCA exercise and which also
help drive the US dollar, we are now able to bridge the
gap between drivers – in other words, predictors and
investment strategies. We will use them not only to
define cross-sectional portfolios that are neutral to the
US dollar, but to also take positions on the US dollar
through time series portfolios. Specifically:

*   Market and sentiment factors, and price action: these
    will be captured through our Momentum and
    Positioning signals. Sections 4.1, 4.5 and 4.6 show
    we effectively capture directional moves in the asset

26 The algorithm, implemented through the function stepwisefit in Matlab,
iterates through the different potential explanatory variables using their p-
value as metric.
27 See, for instance, Capra et al. (2018).
28 We highlight two famous quotes. The first is "Having endeavored to
forecast exchange rates for more than half a century, I have

understandably developed significant humility about my ability in this area",
dated 2001. The second is from 2002: "We at the Federal Reserve have
spent an inordinate amount of time trying to find models which would
successfully project exchange rates [...]. It is not the most profitable
investment we have made in research time. Indeed, it is really remarkable
how difficult it is to forecast."

Page 7
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

class as a whole as well as in individual currencies,
using both price and non-price data.

*   Carry: this factor has now been validated by both
    PCA and panel regressions. Section 4.2 goes through
    our proposed implementations.

*   Monetary policy: we proxy this driver through our
    Momentum Spill-Over factor, previously addressed
    in our research (Natividade et al. (2015)) and revised
    in detail in Section 4.4.

*   PPP, long-term interest rate parity and long-term past
    returns: these will be captured through our Value
    signal. Section 4.3 will show how our fundamental
    valuation signal, albeit more complex than a long-
    term price-based signal, captures the long-term
    reversal phenomena more accurately.

# 3. Assessing Predictive Power and
# Rebalancing Implications

Having identified the core drivers of currency returns,
we next devise an analytical framework that assesses
predictability from a practical angle. For every factor, we
first calculate a signal; in other words, a noise-filtered
estimate of what the factor is "saying” about each asset.

Once the signal is defined, our framework uses the
term structure of its predictive power to identify each
signal's optimal implementation format.

For a given asset, we evaluate the covariance between
future returns and current signal value, using the whole
signal history. We calculate the statistic for the asset
class as a whole, either using the original asset-specific
signals or their values as a spread to the cross-sectional
median. This therefore allows us to conclude on the
most optimal portfolio implementation format - be it
time series, cross-sectional or both.²⁹

This particular implementation question is key to the
systematic investor. Cross-sectional constructs imply
market neutrality - that is, returns should be unrelated
to the US dollar. In this case, the notional (or risk) capital
allocated to the short positions normally equate that of
the longs. Time series constructs are unconstrained and
can take significant directional exposures to the USD.

The CTA community is known for implementing time
series strategies, while the equity long-short community
is known for the cross-sectional approach.

But there are other applications to this framework.
Repeating the exercise across multiple horizons³⁰ allows
us to assess the speed of signal decay. We may
therefore determine whether the signal requires extra
treatment - such as filtering and noise control, as is the
case with fast signals - or how often we should
rebalance a strategy that implements this signal.

It also allows us to better assess the complementary
ability of a given signal in a multi-strategy context,
adding multi-horizon diversification to our multi-factor,
multi-asset currency portfolio.

We estimate two versions of these modified information
coefficients (MIC)³¹: time series and cross-sectional. For
the former, the MIC is estimated as follows:

$$
\text{MIC}_{t,h}^{\text{TS}} = \text{E}\left[\frac{r_{t+h} S_t}{\sum_{i=1}^N S_i^2}\right]
$$

where $S_t$ is the raw signal for a given currency pair at a
given point in time, $r$ represents future returns and $h$ is
the horizon of future returns. In the case of the cross-
sectional MIC:

$$
S_t^{\text{CS}} = S_t - \text{median}(S_t)
$$

$$
\text{MIC}_{t,h}^{\text{CS}} = \text{E}\left[\frac{r_{t+h} S_t^{\text{CS}}}{\sum_{i=1}^N (S_i^{\text{CS}})^2}\right]
$$

The MICs introduced in this section will be applied to
each signal introduced in Section 4, thereby allowing us
to design strategies that capture its information content
more accurately.

An important observation worth highlighting is that our
implementation decisions are subjective; we do not
apply hypothesis tests to define the significance of our
MIC estimates. This is because the relationship between
current signal and future asset returns may be regime-

29 While information coefficients have been carefully addressed as far back
as Grinold and Kahn (1999), we found Hassan and Mano (2013) to be the
most useful recent reference. The authors use this technique - based on
covariances and not correlations - to dissect the carry trade and forward
bias anomalies. According to the authors, the covariance between future
FX returns and current signal can be decomposed into (a) a static
component, (b) a dynamic component and (c) a US dollar (market)
component. Cross-sectional strategies capture (a) and (b), whereas time
series strategies capture (b) and (c).
30 As with Section 2, we apply statistical averaging for horizons other than
daily. This is done through a sampling procedure; for a given horizon, each
MIC estimate is generated using non-overlapping returns with distinctly
different start dates. For example, the final 3-month MIC is an average of
63 separate MIC estimates, each generated using a separate start date.
31 Information coefficients are typically estimated using correlations, and
not co-variances. We made this modification to allow for a comparison
between time series and cross-sectional implementations.

Page 8
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

dependent, which is not captured by current estimates.
This will be covered in future research.³²

Finally, we also assess the impact of portfolio
rebalancing assumptions on the performance of our
return streams. While we do not discuss market impact
models in this report³³ - they are arguably less crucial for
low frequency strategies applied to highly liquid markets
- we evaluate the impact that different rebalancing
assumptions have on return characteristics.

We do so because for every strategy there is a fine
balance between turnover control, which dampens cost,
and turnover enhancement, which increases adaptivity.
There is no widely agreed formula for estimating signal-
to-noise ratios in finance,³⁴ but we can observe the
relationship between these two forces by looping
through different assumptions on portfolio rebalancing
and tranching. In addressing this question we ultimately
seek to identify the optimal rebalancing frequency for
every factor portfolio introduced.

# 4. Building Absolute Return Portfolios

Having identified the core drivers of currency returns,
and a framework for optimal implementation, we now
build absolute return strategies.

Given the unconstrained nature of such portfolios, we
will exploit market directional and market neutral
strategies alike. As mentioned earlier, our decision
criterion is largely based on the predictivity
characteristics of each signal; in other words, it is based
on a form of feature importance.³⁵

We will introduce each factor strategy according to
relevance and horizon, starting with the medium-term

base factors (Trend and Carry) and moving to long-term
Value and short-term factors later.

All factors have a "global" and a "local" element to
them³⁶, in the sense that they can affect all assets in a
similar direction - i.e. USD-related - but also that there
may be key differences between how individual assets
are impacted. As such, we implement both time series
and cross-sectional strategies, and the MICs introduced
in Section 3 allow us to see what is appropriate for each
factor.

## 4.1 Momentum

Momentum is the first of our investment factors. It is
based on the premise that assets that are rising in value
will continue to rise, and those that are falling in value
will continue to fall.³⁷

### 4.1.1 Signal generation

Our trend signal is based on the premise that signal
direction, not signal intensity, is what carries most
predictive power as highlighted in Natividade et al.
(2013) and Natividade et al. (2016). The low entropy in
signal intensity allows us to simplify the raw signal, and
deploy complexity at later stages of the strategy.

As also highlighted in Natividade et al. (2013), our
results suggest that fine tuning the signal training
windows is less optimal relative to an approach that
equally weights between short, medium and longer term
training windows.³⁸ For a given currency pair, our signal
is therefore built using the following steps:

(1) We calculate the total return - spot and carry -
    between $t-h$ and $t$, where $h \in \{21,...,252\}$ is
    measured in business days. This gives us 232 total
    return values.³⁹

32 We believe there are 3 ways a signal should be assessed: (a) overall
predictivity, (b) adaptivity - predictivity under shorter horizons, under both
calendar time and regime time, and (c) diversification potential -
predictivity under distinct market regimes. The current assessment
focuses exclusively on (a) and parts of (b), as it only evaluates the linear
relationship between current signal and future returns. Applying
hypothesis tests on current MICs to define whether or not to use a signal
would over-simplify the problem.
33 The reader should refer to Grinold & Kahn (1999) and, to some extent,
Weng (2017) for that.
34 Lopez de Prado (2018), for instance, addresses somewhat related
concepts through ratios based on a so-called "confusion matrix": precision,
recall, accuracy and F1 score. The author also quotes various metrics
pertaining to the entropy of a time series, which relate to this topic as well.
Grinold and Kahn (1999) use information coefficients - the correlation
between current signals and future cumulative returns, evaluated cross-
sectionally in a portfolio at every point in time - as a somewhat analogous
measure, as also used in Natividade et al. (2016). In electronic engineering,
on the other hand, there is a widely agreed formulae for signal-to-noise
ratios (see, for instance, https://en.wikipedia.org/wiki/Signal-to-noise_ratio).
35 We use the terminology from Lopez de Prado (2018), though our
assessments do not utilize his proposed cross-validation methods as we

believe those are not applicable to our tests. Further, our signals do not
involve optimized calibration.
36 This terminology follows Baz et al. (2013). The authors argue that,
assuming linear signals, cross sectional portfolio weights are equal to time
series weights minus the cross sectional average, and this average can be
considered as a global factor.
37 This description may appear simplistic, but it an accurate summary.
Theories of irrational preferences - under-reaction, herd behaviour and
extrapolation - appear most popular among the explanatory factors behind
the trend premium. The reader interested in the academic literature should
check Jussa et al. (2012), Ilmanen (2011), Moskowitz et al. (2011) and
Natividade et al (2013) for a review of the literature.
38 The results from Section 4.1.2 may favour shorter training windows in
foreign exchange relative to other asset classes, but we opt against it as
the benefits of a one-size-fits-all algorithm for trend following across asset
classes outweighs the losses. In our view, sub-1 month momentum
dynamics in USD/FX should be captured via specific short-term
momentum models, with different signal estimation, noise control,
rebalancing and turnover characteristics.
39 This signal is slightly different from the one introduced in Natividade et
al. (2013), in that previously we used 9 lookback windows between 2
weeks and 1 year, thus generating 9 binary readings ({-1,+1}). We applied

Page 9
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

(2) We record the sign of each total return value from
    Step (1). That is, $S_{t-h,t} = \text{sign}(r_{t-h,t})$.

The raw signal is the average of all 232 signs from Step
(2), i.e. $S_t = \frac{1}{(251-32)} \sum_{h=32}^{251} S_{t-h,t}$. Note that $S_t$ is
bounded, that is, $\hat{s} \in [-1,1]$. We also record the volatility
of $\hat{s}$, $\tilde{\sigma}_t = \sqrt{\frac{1}{232} \sum_{h=32}^{251} (S_{t-h,t} - \bar{s}_t)^2}$, which will be
used later for noise control. Finally, we also record the
sign of the raw signal, $\hat{s}_t = \text{sign}(s_t)$.

### 4.1.2 Signal predictive power

Having defined our Momentum signal, we now estimate
modified information coefficients (MICs) so as to better
understand its relationship to future asset returns. Such
understanding will allow us to address general
implementation questions, such as format - time series
versus cross-sectional - and rebalancing, a function of
signal decay.

> Figure 9: Momentum signal - modified information
> coefficient
[Figure: A bar chart comparing time-series and cross-sectional modified information coefficients for the Momentum signal across horizons (1D, 1W, 1M, 3M, 6M, 1Y).]

Source: Deutsche Bank

Figure 9 shows the progression of our MICs over
multiple horizons, using 28 years of data. It shows
positive predictive power in both time series and cross-
sectional formulations, with the former being notably
higher than the latter especially in the shorter-term.

The key argument favouring time series implementation
lies in the tendency of the US dollar - the closest to a
"market" concept for foreign exchange - to trend. Figure
10 shows the result of a long-term impulse-response

function⁴⁰ applied to the first principal component of the
USD/FX basket⁴¹ , with multiple look-back (impulse)
windows and multiple look-ahead (response) windows⁴².
The numbers in the cells correspond to univariate t-
statistics.

> Figure 10: Impulse-response function t-statistics,
> USD/FX PC1

| | 1W | 2W | 3W | 1M | 2M | 3M | 4M | 5M | 6M | 7M | 8M | 9M | 10M | 11M | 1Y | 2Y | 3Y | 4Y | 5Y |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1W | 1.2 | 1.3 | 2.0 | 2.3 | 3.1 | 2.7 | 2.9 | 2.3 | 2.2 | 2.0 | 1.5 | 1.6 | 1.7 | 1.8 | 1.9 | 1.7 | 1.2 | 1.1 | 0.8 |
| 2W | 0.9 | 1.4 | 1.9 | 2.4 | 2.8 | 2.6 | 2.6 | 2.1 | 2.1 | 1.8 | 1.4 | 1.5 | 1.6 | 1.8 | 1.8 | 1.7 | 1.2 | 1.1 | 0.7 |
| 3W | 1.2 | 1.5 | 2.0 | 2.4 | 2.5 | 2.7 | 2.5 | 2.1 | 1.9 | 1.6 | 1.4 | 1.4 | 1.6 | 1.8 | 1.7 | 1.7 | 1.2 | 1.0 | 0.7 |
| 1M | 1.1 | 1.6 | 2.0 | 2.3 | 2.3 | 2.5 | 2.3 | 1.9 | 1.8 | 1.4 | 1.3 | 1.3 | 1.5 | 1.7 | 1.6 | 1.7 | 1.2 | 0.9 | 0.6 |
| 2M | 1.1 | 1.4 | 1.5 | 1.6 | 1.9 | 1.9 | 1.6 | 1.4 | 1.2 | 1.0 | 1.0 | 1.1 | 1.3 | 1.4 | 1.3 | 1.5 | 1.0 | 0.6 | 0.4 |
| 3M | 0.8 | 1.1 | 1.3 | 1.5 | 1.6 | 1.5 | 1.3 | 1.1 | 0.9 | 0.8 | 0.9 | 1.0 | 1.1 | 1.1 | 1.0 | 1.3 | 0.9 | 0.5 | 0.3 |
| 4M | 0.7 | 1.0 | 1.1 | 1.2 | 1.2 | 1.2 | 1.0 | 0.8 | 0.7 | 0.7 | 0.8 | 0.9 | 0.9 | 0.9 | 0.9 | 1.2 | 0.7 | 0.3 | 0.2 |
| 5M | 0.6 | 0.8 | 0.9 | 1.0 | 1.0 | 0.9 | 0.7 | 0.6 | 0.6 | 0.6 | 0.7 | 0.8 | 0.8 | 0.8 | 0.7 | 1.1 | 0.6 | 0.2 | 0.1 |
| 6M | 0.5 | 0.6 | 0.7 | 0.8 | 0.8 | 0.7 | 0.6 | 0.5 | 0.6 | 0.6 | 0.6 | 0.7 | 0.7 | 0.7 | 0.6 | 1.0 | 0.5 | 0.1 | 0.1 |
| 7M | 0.4 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | 0.5 | 0.5 | 0.6 | 0.6 | 0.6 | 0.6 | 0.5 | 0.9 | 0.5 | 0.1 | 0.0 |
| 8M | 0.3 | 0.4 | 0.5 | 0.5 | 0.5 | 0.6 | 0.6 | 0.5 | 0.5 | 0.5 | 0.5 | 0.6 | 0.6 | 0.6 | 0.6 | 0.9 | 0.4 | 0.0 | 0.0 |
| 9M | 0.3 | 0.4 | 0.4 | 0.5 | 0.5 | 0.7 | 0.7 | 0.6 | 0.7 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | 0.8 | 0.4 | 0.0 | -0.1 |
| 10M | 0.3 | 0.4 | 0.5 | 0.5 | 0.6 | 0.6 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.6 | 0.6 | 0.6 | 0.7 | 0.4 | 0.0 | -0.2 |
| 11M | 0.3 | 0.4 | 0.5 | 0.5 | 0.6 | 0.6 | 0.6 | 0.5 | 0.5 | 0.5 | 0.6 | 0.6 | 0.6 | 0.6 | 0.6 | 0.7 | 0.4 | 0.0 | -0.3 |
| 1Y | 0.2 | 0.3 | 0.3 | 0.4 | 0.4 | 0.5 | 0.4 | 0.4 | 0.4 | 0.4 | 0.3 | 0.3 | 0.3 | 0.3 | 0.2 | 0.1 | -0.2 | -0.5 | 0.9 |
| 2Y | 0.1 | 0.2 | 0.2 | 0.2 | 0.2 | 0.3 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | -0.1 | -0.5 | -0.8 | -1.0 |
| 3Y | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.0 | 0.0 | 0.0 | -0.1 | -0.1 | -0.1 | -0.2 | -0.2 | -0.2 | -0.3 | -0.5 | -0.7 | -0.9 |
| 4Y | 0.0 | 0.0 | 0.0 | 0.0 | -0.1 | -0.1 | -0.1 | -0.2 | -0.2 | -0.2 | -0.2 | -0.2 | -0.2 | -0.2 | -0.3 | -0.4 | -0.4 | -0.5 | -0.7 |

Source: Deutsche Bank

The results show us that:

*   The USD/FX PC1 exhibits trend properties across
    most horizons in the short and medium term, if the
    moves are evaluated relative to short and medium
    term history.
*   At the same time, the USD/FX PC1 exhibits reversal
    properties across long-term horizons when the
    moves are evaluated relative to a long term history.
*   The strongest trend properties lie in short-term
    horizons, under 3 months, and the strongest reversal
    properties lie in horizons beyond 3 years.
*   The t-statistic values are generally low, but this is
    largely due to the use of one series alone (as opposed
    to a panel of multiple series), the fact that the data
    has not been smoothed (so as not to introduce
    memory effects), and the relatively short history
    (mostly affecting the long horizons).

Figure 9 validates taking a time series momentum
approach to FX, but it does not remove cross-sectional
momentum. The US dollar may be a key source of
trendiness, but our MICs also suggest there may be
enough non-USD momentum to validate the
construction of a market neutral strategy.

this change so as to smooth out the signal and therefore require less noise
control.
40 In other words:$r_{t+A,t+1} = a + b \times r_{t-L,t} + \varepsilon_{t+A}$
where $A$ is the look-ahead period (in days) and $L$ is the look-back period (in
days). We used data from January 1980 onwards. We applied non-
overlapping windows and a sampling metric in line with that of Section 1,
thereby reducing discretization error.
41 Daily returns, includes both carry and spot returns.
42 We opted for this simple, univariate impulse-response function as it
makes it easier to visualise the relevant relationships. We also refer the
interested reader to Natividade et al. (2015), where we apply a more
hollistic multivariate, auto-regressive, regime-switching model to the same
problem.

Page 10
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

As such, we first isolate idiosyncratic momentum by
focusing on residual returns; in other words, we strip out
the USD-related returns from each USD/FX pair.⁴³ After
that, we re-build the signal as defined in Section 4.1.1
but using residual returns instead.

### 4.1.3 Noise control

Noise control is a common feature in price action
strategies, and is typically done either through
smoothing the raw signal or attaching level thresholds
below which the new signal is not executed.

We implement noise control for both time series and
cross-sectional signals, and we do it in two steps. First,
we apply a hysteresis-based threshold mechanism
similar to that from Natividade and Anand (2016): if the
absolute raw signal $|\hat{S}_t|$ < $\theta = 1/3$, we keep the old
signal.⁴⁴ This adjustment leads to lower turnover versus
a version with no turnover, which we favour.⁴⁵ The
preliminary signal is, therefore:

$$
\hat{S}_t =
\begin{cases}
\text{sign}(S_t), & S_t \ge 0 \\
\hat{S}_{t-1}, & S_t < 0
\end{cases}
$$

Second, we deflate the preliminary signal by signal
dispersion; in other words, we deflate it by the volatility
of the raw signal as calculated in Section 4.1.2.⁴⁶ This
second adjustment is new, and based on our experience
diagnosing the differences between broad and narrow
trend following programmes.⁴⁷ This gives our final
signal:

$$
S_t = \frac{\hat{S}_t}{\tilde{\sigma}_t}
$$

> Figure 11 plots the contemporaneous relationship
> between aggregate signal volatility and the annual
> returns of our trend following strategy, using data since
> 1991. The relationship is strong, as shown by the
> regression fit, thus validating the approach.

> Figure 11: Contemporaneous relationship between
> dispersion of trend signals and returns of the portfolio
[Figure: A scatter plot showing 1-year strategy return against 1-year average signal dispersion, with a regression line and R-squared value.]

Source: Deutsche Bank

### 4.1.4 Weighting scheme: time series Momentum

As highlighted in Grinold and Kahn (1999), the risk-
adjusted returns in a strategy are a function of the
predictive power of its signals (the rank coefficient) and
how diversified the positions are (the investment
breadth).⁴⁸ As per Natividade et al. (2016), trend
following signals tend to have low predictive power and
we therefore aim to maximise breadth.

Therefore, in theory, one should aim to maximise
breadth when building a trend following algorithm.

At the same time, we must be conscious of the risks of
over-parameterisation and, crucially, also assess
whether there exist thresholds under which breadth
maximising methods are unlikely to add value.

To address these issues, we rigorously compared 2
weighting schemes: inverse volatility (IVW) and
minimum correlation (MCW).⁴⁹ As our pool of assets is

43 The residual returns are estimated as: $\varepsilon_i = r_i - \beta_i r_i^{\text{mkt}} - \alpha_i$, where $r_i$ is the daily return in USD/FX, $r_i^{\text{mkt}}$
is the daily return in the "market" factor (PC1 of USD/FX), and $\beta_i, \alpha_i$ are
the slope and constant terms estimated by a regression using a 1-year
lookback window.
44 This is somewhat different from Natividade and Anand (2016) in that
here we use symmetric thresholds to introduce long and short positions,
as opposed to the prior asymmetric thresholds. The prior rationale, which
reflected the regime-dependent noise profile of investment assets, was
effective in addressing discretisation issues in the old signal. Such has
become less relevant in the new signal as it is far more continuous. The
threshold level of 1/3 followed what had been done in Natividade and
Anand (2016), which in turn was based on our anecdotal evidence of
typical noise thresholds among industry participants.
45 Daily turnover fell from 5.9% to 5.7%, and the backtested historical
Sharpe ratio rose from 0.35 to 0.4.
46 We also set a lower boundary for this volatility estimate, which equals
the 25th percentile of the distribution of signal volatility estimates across all
assets. This is in order to ensure the final signal is not hyper-inflated due to
this noise adjustment, as the adjustment goes in the denominator.

47 For instance, the differences between the DB Cross Asset Trends Index
(<DBCATUSD Index> on Bloomberg), which uses 17 assets, and the same
version that uses 80 assets or the SG Trends Index (former New Edge
Trend Following Index). The CAT version with 80 assets, as well as the
benchmarks, underperformed the DB CAT index since its launch in May
2015 despite benefiting from greater investment breadth. This is largely
due to the difference in noise characteristics.
48 As per fundamental law of active management, Sharpe $\approx$ IC $\times \sqrt{\text{breadth}}$
where IC is the information coefficient and, according to Grinold and Kahn
(1999), breadth is defined as "the number of independent forecasts of
exceptional return we make per year". As per authors, more breadth helps
diversify residual risk.
49 The reader may wonder why have we not attempted other risk-based
weighting schemes, such as those shown in Mesomeris et al. (2012) and
Natividade et al (2013). Our response is two-fold. First, we wanted to test
two extremes: an algorithm that mostly heavily focuses on asset
correlations (MCW), and one that fully ignores correlations (IVW). Other
risk-based algorithms normally sit in between. Second, it is our anecdotal
evidence - and evidence from simulated data in this project - that the less
the number of assets, the less utility that complex weighting schemes
have versus simpler schemes. The pool of assets used here is quite small
compared to, say, the Equities or corporate fixed income pools.

Page 11
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

fixed at 24 currency pairs, we used pairwise correlations
as our measure of diversification potential and therefore
evaluated the effect of changes in this metric on each
weighting scheme.

IVW is the simplest risk-based position weighting
scheme, and therefore a benchmark. It indirectly
enhances diversification by ensuring that position sizes
solely reflect the inverse of the volatility of the asset.
Leaving aside time-related notations, for asset $i$ where
$i \in \{1, ..., N\}$ and with returns $r_i$, the IVW weight is
calculated as:

$$
w_i^{(iv)} = \frac{1/\sigma_{r_i}}{\sum_j 1/\sigma_{r_j}}
$$

MCW, on the other hand, directly targets diversification
by overweighting positions that are less correlated to
others. We implemented the algorithm in Varadi et al.
(2012), as follows:

(1) Compute the exponentially weighted Pearson
    correlation matrix, $\rho$, of asset returns. For
    consistency, we used the same correlation matrix as
    elsewhere in the report, hence see Section 1.2 for
    details.

(2) Compute the mean, $\mu_\rho$, and the standard deviation,
    $\sigma_\rho$, of all elements of the correlation matrix in Step
    (1).

(3) Create the adjusted correlation matrix, $\rho_A$, by
    transforming each element of the previous
    correlation matrix to a reading between $[0,1]$, where
    $-1 \to 0$ and $1 \to 1$. The mapping is done through the
    standard normal cumulative distribution:
    $W_t = 1-\text{normcdf}(\rho_{i,j}, \mu_\rho, \sigma_\rho)$.

(4) Compute the average value for each row of the
    adjusted correlation matrix, $\rho_A$. These are the initial
    portfolio weight estimates from the transform $w_r$ in
    Step (3).

(5) Compute the rank portfolio weight estimates:
$$
W_{\text{Rank}} = \frac{\text{Rank}(w_r)}{\sum_j \text{Rank}(w_r)}
$$

(6) Combine the rank portfolio weight estimates from
    Step (5) with the adjusted correlation matrix from
    Step (3) by multiplication and standardisation:

$$
\hat{W} = \frac{W_{\text{Rank}} \times \rho_A}{\sum W_{\text{Rank}} \times \rho_A}
$$

(7) Scale the portfolio weights by asset volatility and
    further standardise such that the sum adds to 1:

$$
W_i = \frac{\hat{W}_i / \sigma_i}{\sum_j \hat{W}_j / \sigma_j}
$$

One may rationally challenge the inclusion of IVW in our
tests; if we are exclusively interested in maximising
breadth, we should directly opt for diversification-
maximising algorithms such as the MCW.

But our experience suggests that it is not as simple. As
alluded to earlier, diversification-maximising algorithms
may bring drawbacks such as more parameters and
over-allocation to noisy assets.⁵⁰ And while we
addressed the latter in Section 4.1.3, it does not decide
which weighting scheme to choose for us.

The answer should, ideally, come from testing the
sensitivity of our results to the diversification potential
available in the asset pool. With that in mind, it is clear
that historical backtests are not enough.⁵¹ Recent
literature may have shed some light, but the approaches
proposed are also often less applicable to alternative risk
premia strategies.⁵²

As such, we opted for creating simulated data and using
that to build portfolios, which were then compared to
one another using different weighting schemes and
correlation assumptions. Each of the 24 simulated time
series had the same long-term return and volatility equal
to that of the average of our currency pairs,⁵³ and
interacted with one another through a correlation
parameter that varied according to each trial. In other
words:

$$
dX_t = \mu_X X_t dt + \sigma_X X_t dW_t^X
$$

$$
dY_t = \mu_Y Y_t dt + \sigma_Y Y_t dW_t^Y
$$

$$
dW_t^X dW_t^Y = \rho dt
$$

50 Noisy assets are often less correlated and hence increase
diversification. In this case, however, the overall impact is negative; the
information coefficient drops by more than the (square root of) breadth
rises.
51 The two weighting schemes produce very similar risk adjusted returns.
This alone may favour the IVW approach, as it has less parameters, but
that is not enough as historical Sharpe ratios may not accurately reflect
future Sharpe ratios.
52 The recent literature typically focusses on fitting risks, and proposes
methods based on cross validation and on deflating expected performance
by the number of parameter combinations tried. Lopez de Prado (2018) is a

good reference. The challenge in incorporating such techniques to low
frequency, alternative risk premia strategies, is two-fold: (1) it is often
difficult to document how many iterations have been tried on the same
model, and what constitutes an independent iteration, and (2) it is often
difficult to remove memory effects when preparing the data for a sampling
exercise, as different parts of the model will have different memory
dependencies.
53 We opted for an individual long-term return and volatility estimate for all
simulated series, as opposed to one for every simulated asset that
corresponded to that of each real asset, in order to further isolate the
effect of correlations in our results.

Page 12
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

In each trial, we simulated 8,000 observations⁵⁴ for each
of the 24 time series, with a given average correlation
rho to one another. At each rebalancing date, which
occurred at every new time unit, we applied the
aforementioned trend following algorithm and
aggregated positions according to both IVW and MCW
schemes, therefore rebalancing all the prior positions.
The process was repeated 150 times for each fixed
correlation level. We then changed the correlation
assumption above and verified the effect of that on the
difference in risk-adjusted returns of the trend following
portfolios using both IVW and MCW schemes.

Figure 12 plots the result of our analysis. It shows the
difference in Sharpe ratios between the simulated IVW
trend following portfolio and the simulated MCW trend
following portfolio, for a given assumption on the
average correlation between constituents. It tells us
that:

*   When correlations are generally low, the MCW
    scheme underperforms IVW. Higher diversification
    generally implies lower convexity; if the portfolio is
    already diversified to start with, seeking further
    diversification leads to a drop in returns that
    outweighs the drop in volatility. To our surprise, the
    simulations suggest that the correlation threshold to
    switch between schemes is rather high - circa 50%.

*   But when assets are heavily correlated to one
    another, the marginal diversification brought by
    MCW over IVW makes a material difference, and
    therefore it should be recommended. In a pool of 24
    assets and when Trend Following (time series
    Momentum) is the strategy in question, the
    simulations suggest the threshold is circa 50%.

Given the results above, we opted to weight individual
positions using the inverse volatility scheme. As such, at
every rebalancing date, we divide the final signal
calculated in Section 4.1.2 by the volatility of asset
returns, which gives us the preliminary asset weight. We
then modify this preliminary weight to account for
constraints, thereby giving us the final weight.⁵⁵ In other
words, for currency pair $i$ of a total of $N$ currency pairs:

$$
W_{i,t}^{\text{Trend}} = \frac{S_{i,t} / \tilde{\sigma}_{i,t}}{\sum_j |S_{j,t} / \tilde{\sigma}_{j,t}|}
$$

> Figure 12: Difference in Sharpe ratios – IVW and MCW
> schemes using simulated data and different asset
> correlation assumptions
[Figure: A line chart showing the IVW (-) MCW Sharpe ratio spread across different levels of correlation among assets, indicating underperformance of MCW at lower correlations.]

Notes: see main text for details. Source: Deutsche Bank

### 4.1.5 Weighting scheme: cross-sectional Momentum

Deriving asset weights in the cross-sectional
Momentum strategy can be a simpler exercise; not only
it should focus primarily on USD neutrality, but our
previous results also showed there is no need for asset
weights to reflect signal intensity.

The steps, at a given rebalancing date, are as follows:

(1) We rank currency pairs based on the signals
    estimated in Sections 4.1.1 and 4.1.3, but now
    utilizing residual returns (instead of original returns)
    and without the sign in the raw signal. In other
    words:

$$
S_{t,\text{res}}^{\text{res}} =
\begin{cases}
S_{t,\text{res}}, & S_{t-1,\text{res}} \ge 0 \\
\hat{S}_{t,\text{res}}, & S_{t,\text{res}} < 0
\end{cases}
$$

$$
\hat{S}_t^{\text{res}} = \frac{S_t^{\text{res}}}{\tilde{\sigma}_t}
$$

(2) We go long the top half and short the bottom half
    of assets in our pool, assigning equal weights to
    each asset such that the absolute sum of weights
    equals 100%. We opt for taking exposure to all a
    ssets so as to maximise factor exposure and avoid
    idiosyncratic risk.

(3) We re-adjust the weights from Step (2) such that
    the net beta to the US dollar is zero:

54 Equivalent to 32 years of data, if daily, thereby resembling the length of
much of our data.
55 We attach upper and lower boundaries for each currency pair. The
upper boundary is equal to the minimum of 15% and 2% of the currency's
average daily volume for a portfolio of USD 1bn. The lower boundary is the

same as the maximum, but with a negative sign. Absolute weights must
sum to 100%.

Page 13
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

$$
\arg \min_w \sum_{i=1}^N (w_i - \tilde{w}_i)^2, \text{ such that } \sum w_i \beta_i = 0
$$

where $\tilde{w}_i$ is the initial USD/FX weight and $\beta_i$ is the
beta of each currency pair to the PC1 of the asset
class.⁵⁶

The reader may question the need for beta neutralisation
given that the original signal is already calculated using
non-USD returns. While it is a fair question, our
backtests strongly indicated the need for an additional
adjustment. USD-neutrality in the signals may not
translate into USD-neutrality in the portfolio.

### 4.1.6 Portfolio tranching

Having defined our signal and weighting schemes, we
next move on to define the optimal rebalancing
frequency for our Momentum portfolios.

> Figure 13 shows our results in more detail, as it
> evaluates the effect of our rebalancing assumptions on
> risk-adjusted returns, turnover and cost. The numbers
> are not surprising; backtests that rebalance more
> frequently generally show better risk-adjusted returns
> before costs, as per blue bars, but higher turnover, as
> per orange line. The higher turnover translates into
> higher costs.

> Figure 13: Tranching results (time series followed by
> cross-sectional constructs) – Momentum portfolios
[Figure: Two bar charts showing Sharpe (w/o cost) and Sharpe (w/ cost) and Daily effective T/O (rhs) for Momentum portfolios across rebalancing frequencies (Daily, Weekly, Monthly, Quarterly), for both time series and cross-sectional constructs.]

Source: Deutsche Bank

As we aim to strike a balance between adaptivity and
turnover, we choose the portfolio that rebalances
monthly, using 20 daily tranches. Not only it maintains
the high backtested Sharpe ratio, suggesting that signal
entropy is still largely reflected in the positions, but the
daily effective turnover also drops by more than three-
quarters from the fastest rebalancing alternative. This
particular momentum signal does not need to be "fast";
faster signals will be introduced later in this report. We
make this decision for both time series and cross-
sectional implementations.

### 4.1.7 Backtest performance

> Figure 14 displays the historical backtest of our USD/FX
> Momentum strategies, with transaction costs included.
> The time series strategy is heavily market-directional;
> while long-term correlations to the USD Index reside at
> 6%, 1-year rolling correlations (of daily returns) swing
> significantly over time as shown in Figure 15. The
> cross-sectional Momentum strategy is, however, far less
> correlated over time as expected given the explicit beta
> neutralisation.

> Figure 14: Time series and cross-sectional Momentum
> backtested returns (net of transaction costs)
[Figure: A line chart showing the backtested returns of time-series (SR: 0.60) and cross-sectional (SR: 0.46) Momentum strategies over time.]

Source: Deutsche Bank

56 Another alternative for beta neutralization involves estimating the USD-
beta of both long and short baskets separately and using these as hedge

ratios. This approach would however require originally allocating equal risk
weights for each asset as opposed to equal USD weights.

Page 14
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

> Figure 15: Rolling 1-year correlations to the US dollar
> (PC1 of the asset class)
[Figure: A line chart showing rolling 1-year correlations to the US dollar for cross-sectional and time-series strategies.]

Note: using daily returns. Source: Deutsche Bank

## 4.2 Carry investing

As shown in Section 2, Carry is an indisputable
determinant of foreign exchange returns. It has also
been a popular systematic strategy in the asset class
over decades, and we refer the interested reader to
Ilmanen (2011), Rosenberg (2013) and Koijen et al.
(2013) for a detailed literature review.

Carry directly reflects interest rate differentials between
countries, which - as noted in Anand et al. (2014) and
alluded to in Section 2 - links to currency valuations
through what higher interest rates imply about domestic
economic conditions. If rates are rising due to
deteriorating external balances or rising inflation, then -
as we will show in Section 4.3 - standard valuations
models will suggest that the currency should depreciate
in order for the country to regain competitiveness.⁵⁷

It also implies a strong link between the FX Carry trade
and investor sentiment. To the extent that countries with
higher interest rates also have higher current account
financing requirements, they are more dependent on
capital inflows and their currencies more sensitive to
investor sentiment - particularly in emerging markets. As
such, the investor typically requires a premium - in the
form of positive carry - in order to be long currencies
that are more vulnerable.

### 4.2.1 Signal generation

Estimating FX carry is straight forward. It is a model-free
characteristic observed at the start of a trade, and
represents the expected return of a static FX position
assuming prices stay constant. It is normally⁵⁸ defined
according to 2 exogenous, directly observable variables -
domestic interest rates in the 2 countries. This interest
rate spread defines the distance between spot and
forward rate, thereby defining the carry.

Translating from carry to a signal is also straight forward,
and in our view should reflect 3 characteristics. First and
foremost, both sign and size of the carry value help
predict future asset returns, and therefore carry intensity
should be directly reflected on signal value.⁵⁹ Second,
FX carry values are less noisy, at least as compared to
price action signals; this allows us to apply looser noise
control. Finally, carry and asset volatility typically bear a
positive relationship and therefore the signal should be
deflated by volatility, thereby resembling a modified ex-
ante Sharpe ratio⁶⁰.

Our Carry signal is built as follows:

$$
c_i = (S_i - F_i)/F_i
$$

$$
c_t^{\text{Carry}} = \frac{1}{N-1} \sum_{h=0}^{N-1} c_{t-h} / N
$$

$$
S_{i,t}^{\text{Carry}} = S_{i,t} / \tilde{\sigma}_{i,t}
$$

### 4.2.2 Signal predictive power

Figure 16 confirms our findings from Section 2. Not only
is the Carry factor quite powerful - with higher MICs
than any other signal - but its predictive power also
persists across horizons.

> Figure 16: Modified information coefficients – FX Carry
> signal
[Figure: A bar chart comparing time-series and cross-sectional modified information coefficients for the FX Carry signal across horizons (1D, 1W, 1M, 3M, 6M, 1Y).]

Source: Deutsche Bank

The numbers also suggest that both time series and
cross-sectional implementations add value. The latter is
commonplace in both academic and industry research,
but the former has also gathered attention recently – see,

57 This link helps explain why some authors label the FX Carry trade as FX
Value; an example is Ang (2014).
58 We say normally instead of strictly because this argument does not
apply to non-deliverable (NDF) FX markets. In that case, onshore interest

rates are often unavailable to the foreign investor and do not define the
price of the FX forward.
59 See Maurer et al. (2016) and Natividade et al. (2016).
60 See Anand et al. (2014).

Page 15
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

for instance, Koijen et al. (2013), Lustig et al. (2014) and
Bartram et al. (2018).

### 4.2.3 Weighting scheme: time series Carry

As alluded to earlier, the time series implementation is
akin to capturing the dollar carry; a term coined in Lustig,
Rosanov and Verdelhan (2014). While not as common,
we find this implementation just as valid as the cross-
sectional version. Interest rates are a key variable driving
the US dollar globally⁶¹, and therefore could also be
considered as a means of taking directional views on the
first principal component of the asset class.

Having argued the need for sign and size to be both
reflected into the Carry signal, we also directly translate
these into portfolio weights. The weight allocated to
each asset is therefore as follows:

$$
w_i^{\text{Cr}} = \frac{S_{i,t}^{\text{Carry}}}{\sum_j |S_{j,t}^{\text{Carry}}|}
$$

$$
\hat{w}_i^{\text{Cr}} = w_i^{\text{Cr}} / \sum_j w_j^{\text{Cr}}
$$

Note that asset weights follow the same summation and
boundary constraints as per Section 4.1.4.

### 4.2.4 Weighting scheme: maximum ex-ante Sharpe ratio

Our market neutral implementation of the Carry factor is
inspired by Maurer et al. (2016); in other words, we seek
to maximise the ex-ante risk-adjusted returns of our
Carry portfolio. Therefore, our asset weights are set so
as to maximise the ratio between portfolio carry and
portfolio volatility. The procedure, for a given
rebalancing date, is as follows:

$$
\arg \max_W \frac{\sum w_i C_i}{\sqrt{\sum_i \sum_j w_i w_j \sigma_{i,j}}}
$$

subject to:

$$
\sum_i w_i \beta_i = 0
$$

All other constraints, such as the absolute summation of
weights equalling 100% and individual weights staying
within boundaries, are the same as in Section 4.1.4.

This approach seeks to maximise the contribution of
carry to final strategy returns, while also minimising the
contribution of spot moves. The construct balances the
relationship between risk, as reflected in how each asset
co-varies with the portfolio, and reward, as reflected by
asset carry. Therefore not only it favours assets with a

high carry-to-volatility ratio but also assets whose
diversification properties outweigh their lower carry.

The beta neutralisation constraint is also key to this
construct. While FX spot returns are known to move in
the direction of carry, and not against it⁶², such feature
should only be a part of our time series Carry
implementation. As we show in Section 4.2.6, the
constraint has also made quite a difference. It is an
approach we follow in other asset classes as well.⁶³

### 4.2.5 Portfolio tranching

Having derived our Carry weights, we now define the
rebalancing assumptions by analysing the impact of
tranching, just as we did in the Momentum factor.
Figure 16 shows that the Carry signal does not exhibit
fast decay, and therefore our rebalancing procedure
should focus primarily on turnover - and hence cost -
control.

The backtest results seem to favour weekly rebalancing,
as per Figure 17. That said, the improvement in risk-
adjusted returns is not notably significant and mainly
attributed to volatility reduction. As such, we also opt for
monthly rebalancing - tranched daily, with 20 tranches
in total - as is the case in our Momentum portfolios. We
also opted against slower rebalancing as that could have
adverse implications to our beta estimation and hence
market neutrality.

### 4.2.6 Backtest results

Figure 18 suggests that the Carry portfolios complement
one another, which we also deduce from looking at how
the combined portfolio outperforms the individual
constructs in the backtest.

More importantly, the separate constructs allow us to
take on USD exposure more efficiently. As shown in
Figure 19, the dollar carry - time series construct
exhibits significant correlations to the US dollar over
time, while the market neutral version is largely
uncorrelated.

61 We refer the reader, for instance, to our FX Blueprint reports over the
course of the past 2 decades.
62 See Koijen et al. (2013) and Rosenberg (2013). This is a standard finding
of uncovered interest rate parity tests, which show that UIP does not hold
over the long run. The poor recent performance of FX Carry, which reflects

unconventional monetary policies and floored interest rates, suggests
however that UIP has been holding in recent years.
63 See Anand et al. (2018). Note however that performance using a cross-
sectional approach similar to our Momentum factor yields similar results as
long as the market beta constraint is also present.

Page 16
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

> Figure 17: Tranching results (time series followed by
> max Sharpe constructs) – FX Carry portfolio
[Figure: Two bar charts showing Sharpe (w/o cost) and Sharpe (w/ cost) and Daily effective T/O (rhs) for FX Carry portfolios across rebalancing frequencies (Daily, Weekly, Monthly, Quarterly), for both time series and max Sharpe constructs.]

Source: Deutsche Bank

> Figure 18: Time series and market neutral Carry
> backtested returns (net of transaction costs)
[Figure: A line chart showing the backtested returns of time-series (SR: 0.60) and Max Sharpe (SR: 0.79) Carry strategies over time.]

Source: Deutsche Bank

> Figure 19: Return correlations to the US dollar, 1Y
> rolling
[Figure: A line chart showing rolling 1-year correlations to the US dollar (proxied by PC1 of USD/FX) for time-series and Max Sharpe strategies.]

Note: US dollar proxied by the first principal component of the asset class (USD/FX). Source:
Deutsche Bank

The decoupling between our market neutral portfolio
and USD returns has an additional, positive
consequence: the strategy was largely uncorrelated to
global risk appetite. This results from the US dollar
acting as a historical risk barometer⁶⁴, and therefore
neutralising exposure also made the backtest returns
more sentiment-agnostic. Figure 20 shows the
distribution of monthly backtest returns across regimes
in our Global Sentiment Indicator. The standard cross-
sectional (HML) Carry factor⁶⁵ is far more sensitive to
market regimes. This finding removes the need for
timing mechanisms in our FX Carry factor, thereby
changing our proposed implementation from Anand et
al. (2014).

> Figure 20: Monthly returns according to GSI terciles –
> market neutral versus standard HML Carry portfolio
[Figure: A bar chart comparing monthly returns for Max Sharpe and HML strategies across different GSI terciles (Low, Medium, High).]

Source: Deutsche Bank

64 The US dollar has historically been a safe haven due to relative capital
flows, especially at periods of market risk aversion, although this may not
persist into the future.

65 24 USD/FX pairs, equally weighted, ranked by carry and with the same
rebalancing assumptions as our proposed market neutral portfolio.

Page 17
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

Finally, Figure 21 shows the relative contribution of
carry and spot onto our time series and market neutral
Carry portfolios. We highlight two findings:

*   Spot moves contribute more in the time series
    construct, while carry is more influential in the
    market neutral construct.

*   Spot has made a stronger impact in both portfolios
    since the end of last decade, as unconventional
    monetary policy suppressed global interest rates.

### 4.3 Value investing

Sections 2.1, 2.2 and 4.1.2 all suggest that currencies
exhibit reversal properties over the long run. Value
models help us comprehend such phenomena. They
allow us to understand the long-term swings in the US
dollar, the fact that uncovered interest rate parity often
holds over the long run, and - importantly – why there
are cases where this statement does not apply.

The most standard model of valuation is based on the
law of one price: all identical goods must sell at the same
price in a frictionless world. This creates an intimate link
between domestic and foreign prices. Significant
deviations should be offset by opposite moves in the
exchange rate; if this hasn't occurred yet, it creates a
value opportunity.

The best reference for the law of one price is the
purchasing power parity exchange rate. In other words,
the ratio of domestic prices in an identical basket of
goods between two countries. It is generally agreed that
nominal exchange rates should not diverge significantly
from the PPP exchange rate, and indeed they do not for
many comparable economies. But the less comparable
the countries, the more that nominal exchange rates can
persistently deviate from their PPP anchor.

Much of the work by fundamental currency researchers
focuses on explaining why persistent deviations can
(and do) occur, and whether those explanatory variables
can be included in the original PPP estimate so as to
generate a better, more universal fair value anchor for
any exchange rate. A significant body of academic and
industry literature exists on the topic; Ricci et al. (2008),
Menkhoff et al. (2015), Ca'Zorzi and Rubaszek (2018) are
good examples of the former, and Brehon (2013) and
Kalani (2016) are flagship references of the latter.

The discussion often boils down to two questions: what
estimation format to use and which extra variables best
capture the divergences? Keeping in mind the
challenges with data quality and parameterisation risks,
we opted for a somewhat simple approach that is also
based on the law of one price. Crucially, it also allows us
to compare developed and emerging currencies as part
of the same factor portfolio.

> Figure 21: Annual return attribution to both time series
> and market neutral Carry portfolios
[Figure: Two bar charts showing annual return attribution to Carry and Spot for time-series and Max Sharpe portfolios from 1991 to 2017.]

Source: Deutsche Bank

### 4.3.1 Signal generation

Fundamental Value models naturally carry significant
overfitting risks, which we attribute to 3 reasons. First,
they are based on long-term variables and a thorough
assessment often requires more history than is available.
Second, the revised nature of some inputs may
introduce look-ahead bias. Third, there is often a
significant degree of subjectivity among analysts on
which variables to include in the model. This is not a
problem specific to foreign exchange; Mesomeris et al
(2018), for instance, point out similar issues in Equity
Value.

With that in mind, we opt for a parsimonious signal that
is largely based on Kalani (2016). We first estimate each
currency's fair value and misalignment on a trade-
weighted basis. We then convert to its respective
USD/FX exchange rate and adjust for risk. At a given
rebalancing date, which occurs once a month, the steps
are as follows:

(1) We take the Bank for International Settlements (BIS)
    real broad effective exchange rate (REER) for each
    country. This will be used as dependent variable in
    our panel regressions.

Page 18
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

(2) We estimate a reduced-form long-run relationship
    between the REER and macroeconomic variables in
    question. We regress the REER on 2 variables:
    productivity differentials and terms of trade, using a
    dynamic OLS model:

$$
\log(\text{REER}_{i,t}) = \alpha_i + \beta^1 \times \text{PROD}_{i,t} + \beta^2 \times \text{TOT}_{i,t} + \theta_0 + \varepsilon_{i,t}
$$

$$
\theta_0 = \sum_{s=-1}^1 (\psi_s^1 \text{PROD}_{i,t+s} + \psi_s^2 \text{TOT}_{i,t+s})
$$

$$
\text{PROD}_{i,t} = \log\left(\frac{\text{GDP}_{i,t}}{\text{GDP}_{\text{it}}^{\text{weighted}}}\right)
$$

$$
\text{TOT}_{i,t} = \log(\text{TOT}_{i,t})
$$

where $\text{GDP}_{i,t}^{\text{weighted}}$ is the ratio of real GDP
per capita for country $i$ over the weighted average of real
GDP per capita of the basket of countries. This ratio is
our proxy for productivity differentials, thereby
addressing the Balassa-Samuelson effects. $\text{TOT}_{i,t}$ is the
terms of trade index for country $i$.⁶⁶ $\alpha_i$ captures country
fixed effects. The regressions are done in panel format,
with 5 separate panels (p): EM commodity exporters,
EM commodity importers, East Asian "tigers", G-10
commodity exporters and G-10 commodity importers.

(3) For a given country, we take its REER misalignment
    value, $\varepsilon_{i,t}$, and convert it to its equivalent USD/FX
    exchange rate misalignment.⁶⁷ This is our signal, $S_{i,t}^V$.

### 4.3.2 Signal predictive power

Figure 22 confirms our earlier assumptions that
fundamental Value signals are of a long term nature. The
predictive power does not decay; in fact, it grows with
time. This is also in line with academic literature, which
points to a PPP misalignment half-life of more than 2
years.⁶⁸

Interestingly, the time series MICs are of similar levels
as the cross-sectional MICs, which validates
implementing both strategy constructs. While the latter
is commonplace, the former is not but gives us a view
on broad US dollar over or under-valuation.

### 4.3.3 Weighting scheme: time series Value

Our time series weighting scheme directly reflects the
signal value, but adjusted for asset volatility. Some
assets may look more misaligned simply because they
are more volatile, and therefore we need to adjust for
volatility mismatches. Further, the (risk-adjusted) weight
intensity directly reflects both signal sign and size, as
both add value in this particular investment factor.⁶⁹ This
is also in line with the lines in the sand approach to
currency misalignments⁷⁰; very significant
misalignments matter far more than smaller ones.

> Figure 22: Modified information coefficients – FX Value
[Figure: A bar chart comparing time-series and cross-sectional modified information coefficients for the FX Value signal across horizons (1M, 3M, 6M, 1Y, 2Y).]

Source: Deutsche Bank

The weights in our time series construct are derived as
follows:

$$
S_{i,t}^V = S_{i,t} / \tilde{\sigma}_{i,t}
$$

$$
W_{i,t}^V = \frac{S_{i,t}^V}{\sum_j |S_{j,t}^V|}
$$

### 4.3.4 Weighting scheme: cross-sectional Value

The cross-sectional weighting scheme seeks to achieve
2 objectives: adjust position sizes for specific
misalignment values and achieve market neutrality. The
first is tricky; equal dollar weights or risk weights would
not distinguish currencies that are far misaligned. A raw
signal weighting scheme could also lead to
misspecification; in other words, too much model risk.

To address this issue, we applied a linear weighting
scheme that reflects the ranks of the risk-adjusted
currency misalignment.⁷¹ This construct therefore goes
long the top half of assets, which are most
comparatively undervalued, and short the other half. The
weight allocated to each asset is a linear reflection of
where it ranks versus the other assets in the same half.⁷²

66 Terms of trade is the ratio of export over import prices. We use different
TOT sources depending on whether the country is a commodity exporter
or not. If so, we use the Citibank Commodity Terms of Trade Indices. If
not, we use national source TOT indices.
67 We convert into USD/FX using 2 methods: matrix inversion and least
squares. Cline (2008) explains the approach in detail.
68 See, for instance, Lothian and Taylor (2000) and Ricci et al (2008).
Winkler (2017) also provides an in-depth review of reversals to PPP
exchange rates.
69 See Natividade et al. (2016).

70 See Chadha and Nystedt (2006).
71 A non-linear weighting scheme might have increased idiosyncratic risk
too much, especially given the small number of assets in the investment
pool.
72 Take for instance a basket of 12 currencies that the portfolio is long, as
these are comparatively undervalued in the basket of 24. The most
undervalued gets a weight of $W_1 = 0.5 \times 12 / (12 + 11 + ... + 1) = 7.7\%$
while the least undervalued currency gets the respective weight of $W_{12} =
0.5 \times 1/78 = 0.6\%$. The same calculation applies to the short basket, with
opposite signs.

Page 19
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

As with the previous market neutral portfolios, we re-
adjust the asset weights so as to target a neutral beta to
the US dollar, as proxied by the PC1 of the asset class.

The beta adjustment works as follows:

$$
\arg \min_W \sum_{i=1}^N (w_i - \tilde{w}_i)^2 \text{ such that } \sum w_i \beta_i = 0
$$

where $\tilde{w}_i$ is the linearly-ranked weight for a given asset
and $\beta_i$ represents the currency beta to the USD. The
other constraints are the same as with cross-sectional
Momentum.

### 4.3.5 Portfolio tranching

> Figure 23 is in line with our prior findings; slower
> rebalancing generally outperforms faster rebalancing.
> As such, we opt for annual rebalancing, tranched
> monthly, in the case of the time series portfolio
> construct.

> Figure 23: Tranching results (time series followed by
> cross-sectional constructs) – Fundamental Value
> portfolio
[Figure: Two bar charts showing Sharpe (w/o cost) and Sharpe (w/ cost) and Monthly effective T/O (rhs) for Fundamental Value portfolios across rebalancing frequencies (Monthly, Quarterly, Half-yearly, Yearly), for both time series and cross-sectional constructs.]

Source: Deutsche Bank

The cross-sectional portfolio is, in contrast, rebalanced
monthly, but we do so only in order to ensure our hedge
ratios are sufficiently adaptive and therefore allow for
market neutrality. Note that, due to the nature of our
data sources, monthly is also our fastest available
rebalancing frequency.

### 4.3.6 Backtest results

As is the case with prior factor portfolios, the time series
and cross-sectional implementations complement one
another. As further highlighted by the rolling
correlations the time series portfolio bears significant
USD directionality while the cross-sectional portfolio is
largely market neutral.

> Figure 24: Time series and market neutral Value
> backtested returns (net of transaction costs)
[Figure: A line chart showing the backtested returns of time-series (SR: 0.28) and cross-sectional (SR: 0.66) Value strategies over time.]

Source: Deutsche Bank

Key to the Value factor, however, is the convexity
exhibited by the time series construct. This feature is
particularly attractive, and often sought after in FX Value
portfolios. Its defensiveness - particularly to variations in
the US dollar - can be particularly attractive for currency
risk management programmes.

Page 20
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

> Figure 25: Return correlations to the US dollar, 1Y
> rolling
[Figure: A line chart showing rolling 1-year correlations to the US dollar for cross-sectional and time-series strategies.]

Source: Deutsche Bank

> Figure 26: Convexity – monthly Value portfolio returns
> against monthly US dollar returns
[Figure: A scatter plot showing monthly Value portfolio returns against monthly US dollar returns, illustrating convexity, with a regression line.]

Notes: US dollar proxied by the PC1 of the USD/FX basket, as before. Source: Deutsche Bank

## 4.4 Rates Momentum spill-over

Short-term, or "fast" factors are our final area of
coverage. Not only Section 2 alluded to the presence of
short-term patterns, but the liquidity and depth of
foreign exchange markets also suggests we should be
able to capture them systematically.

Most of the signals in this category point towards short-
term momentum. But not only they do not correlate
heavily with short-term price action momentum, they
also exhibit certain attractive characteristics not seen in
price action signals – namely smoother data and less
memory dependency.

We start with our momentum spill-over (MSO) signal. It
is based on the argument that interest rates have
predictive power in FX, as they directly reflect perceived
shifts in monetary policy and inflation targets.⁷³ Given
the strong predictive power of interest rate spreads on
FX - as per our discussion on Carry – it is no surprise
that its first derivative also contains useful information,
even if it decays fast.

### 4.4.1 Signal generation

The signal, launched in Natividade et al. (2015), is built
using the following steps:

(1) Calculate the interest rate spread between a given
    country and the US as per 6-month FX forwards.
    Record the change over the past 21, 42 and 63
    business days, and annualise these changes.

(2) Calculate the annualised volatility of daily changes in
    6M interest rate differentials, using the same
    lookback windows as in Step (1).

(3) Calculate the ratio of changes, as per Step (1), over
    volatility, as per Step (2), for all 3 windows, and take
    the average of these 3 ratios.

(4) Apply noise control by taking the 1-month average
    of the measure calculated in Step (3). This average is
    our signal, $S_t^{\text{MSO}}$.

As with our Value factor, the spill-over signal requires
further treatment in order to be applicable to a wide pool
of currency pairs. This is because the sign of the
relationship between rates momentum and FX returns
often depends on country risk premium: the higher the
risk, the more that rising rates hurt the currency. That
identity, explained in detail in Natividade et al. (2015),
goes in opposite direction to the pattern we are trying to
capture: that relative central bank hawkishness should
lead to relative currency appreciation.

As such, we implemented a filter that removes currency
pairs from the investment pool when needed. We
calculate the 1-year correlation between (past) 1-day
interest rate spread moves and (future) 1-day FX returns
for each currency pair; if the correlation is negative, that
pair is removed.⁷⁴

### 4.4.2 Signal predictive power

Figure 27 shows how the modified information
coefficients in our momentum spill-over signal change
across horizons. Not only it decays fast, but the levels

73 The interested reader should refer to Rosenberg (2002), Chen et al.
(2009), Ang et al. (2010), and Georges et al. (2014
74 This is a slight modification from the original signal from Natividade et al.
(2015). We formerly ranked all assets according to the signal, allocated
capital according to the ranks, and then re-distributed the capital only to

those assets that passed the filter. The ranking now only takes place after
filtering.

Page 21
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

are generally low. This confirms both the short-term and
momentum nature of the signal. Interestingly, the time
series construct exhibits a shorter term profile than the
cross-sectional construct.

### 4.4.3 Weighting schemes: time series and cross-sectional

The spill-over signal resembles traditional Momentum in
terms of modified information coefficients, which are
also low, and in nature, as it also points towards
continuation. These similarities led us to move away
from our original weighting scheme, introduced in
2015⁷⁵, and instead implement the same approach as
introduced in Sections 4.1.4 and 4.1.5. Other arguments
also favour an implementation that focuses on signal
sign and not on signal size:

*   Low MICs imply that signal intensity is less
    informative.
*   Portfolio turnover is already high due to the fast
    nature of this signal. The weighting schemes applied
    in our Momentum portfolios help reduce
    unnecessary turnover, and therefore cut costs.

> Figure 27: Momentum spill-over signal – modified
> information coefficient
[Figure: A bar chart comparing time-series and cross-sectional modified information coefficients for the Momentum spill-over signal across horizons (1D, 1W, 1M, 3M, 6M).]

Source: Deutsche Bank

At a given rebalancing date, the weight allocated to a
given asset in the time series Momentum Spill-Over
portfolio is calculated as follows:

$$
w_i = \text{sign}(S_t^{\text{MSO}}) \times \frac{1/\tilde{\sigma}_{r_i}}{\sum_{j=1}^N 1/\tilde{\sigma}_{r_j}}
$$

As for the cross-sectional MSO portfolio, the asset
weights are calculated using the same approach as with
the standard Momentum portfolio. In other words:

(1) We rank currency pairs based on the signals
    estimated in Section 4.4.1.

(2) We go long the top half and short the bottom half of
    assets in our pool, assigning equal weights to each
    asset such that the absolute sum of weights equals
    100%. We opt for taking exposure to all assets so as
    to maximise factor exposure and avoid idiosyncratic
    risk.

(3) We re-adjust the weights from Step (2) such that the
    net beta to the US dollar is zero:

$$
\arg \min_w \sum_{i=1}^N (w_i - \tilde{w}_i)^2, \text{ such that } \sum w_i \beta_i = 0
$$

In this case, $\tilde{w}_i$ is the initial USD/FX weight and $\beta_i$
represents the currency beta to the USD.⁷⁶ The other
constraints are the same as with the factor portfolios
described earlier.

### 4.4.4 Portfolio tranching

Rebalancing portfolios of fast factors is tricky as one
needs to preserve signal entropy while also curtailing
noise and costs.

On one hand, the fast signals primarily add value by
adapting quickly to changing market conditions. They
make the total portfolio more adaptive, and therefore
keep the user from trying to accelerate other signals that
are supposed to be slow.

On the other hand, fast factors can be noisy and costly,
and we need to address both issues. The first has
already been covered in Section 4.3.1, as we apply a
moving average to the original signal. But the second is
also pertinent. Figure 28 shows significant decay in risk-
adjusted returns after accounting for transaction costs,
assuming daily rebalancing (i.e. no tranching).

We therefore opt for weekly rebalancing in both time
series and cross-sectional constructs. This allows us to
safeguard signal entropy, while also seeing a significant
drop in average daily turnover and, therefore, costs. The
weekly rebalancing also allows us to keep the hedge
ratios in the cross-sectional portfolio adaptive, and
therefore more market neutral.

### 4.4.5 Backtest results

The first clear finding from our backtests is that this
factor produces worse expectancy than the others. That
said, it also provides positive convexity, with Sortino
ratios that are on average 1.4x the Sharpe ratios⁷⁷, which
reflects the fast adaptivity desired in short-term factor

75 Natividade et al. (2015) uses a non-linear ranked weighting scheme for
capital allocation. The signal was only implemented in a cross-sectional
format, and with no beta targets.
76 Another alternative for beta neutralization involves estimating the USD-
beta of both long and short baskets separately and using these as hedge

ratios. This approach would however require originally allocating equal risk
weights for each asset as opposed to equal USD weights.
77 The backtested Sharpe ratios for the time series and cross-sectional
MSO portfolios are, respectively, 0.33 and 0.34. The Sortino ratios are 0.46
and 0.48.

Page 22
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

portfolios. The two constructs also complement one
another.

Finally, Figure 30 shows that constraining our beta
exposures also led to market neutralisation even in
shorter term factors. We note that the initial strategy
from Natividade et al. (2015), despite being
implemented under a cross-sectional scheme of capital
neutrality, correlates more with the time series version
of the new construct than the cross-sectional version.

> Figure 28: Tranching results (time series followed by
> cross-sectional constructs) – Rates Momentum Spill-
> Over portfolio
[Figure: Two bar charts showing Sharpe (w/o cost) and Sharpe (w/ cost) and Daily effective T/O (rhs) for Rates Momentum Spill-Over portfolios across rebalancing frequencies (Daily, Weekly, Monthly, Quarterly), for both time series and cross-sectional constructs.]

Source: Deutsche Bank

> Figure 29: Time series and market neutral MSO
> backtested returns (net of transaction costs)
[Figure: A line chart showing the backtested returns of time-series (SR: 0.33) and cross-sectional (SR: 0.34) MSO strategies over time.]

Source: Deutsche Bank

> Figure 30: Return correlations to the US dollar, 1Y
> rolling
[Figure: A line chart showing rolling 1-year correlations to the US dollar for time-series and cross-sectional strategies.]

Source: Deutsche Bank

## 4.5 Positioning factors: COFFEE

We now move on to signals linked to investor
positioning, based on exchange traded contracts and
are hence publicly available.

Our first positioning signal is dubbed COFFEE⁷⁸. It was
introduced in Weng and Grover (2017) and is based on
DTCC options flow data. It is based on findings from the
FX literature - notably Evans and Lyons (2002) - that
order flow is an important determinant of exchange
rates. The premise is that so-called "smart money", or
leveraged fund order flows, lead price action, and we
use options volume data to proxy such order flow.

We base the signal on two assumptions, which are
backed by an analysis of randomised trade samples with
internal data:

78 Categorised Option Flow in Foreign ExchangE.

Page 23
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

*   Distinct types of participants have distinct
    preferences for strikes. Funds seeking speculative
    opportunities and effective leverage favour higher
    delta strikes, whereas corporate hedgers tend to
    prefer lower delta options.⁷⁹

*   Most investors are net buyers rather than sellers of
    options.⁸⁰

The signal therefore reflects our proxy for leveraged flow,
using higher delta option volumes. We apply it to a
subset of our original asset pool, namely USD exchange
rates against G10, KRW, PLN, SGD, MXN, ILS, TRY, RUB
and ZAR.⁸¹

### 4.5.1 Signal generation

As per Weng and Grover (2017), the signal for a given
currency pair is calculated daily, as follows:

(1) We calculate option deltas for all European options
    expiring in less than one year⁸², and select options
    whose (absolute) deltas range between 0.25 and
    0.75.

(2) We calculate the difference between notional
    volumes, traded on aggregate over the past 4 weeks,
    of the calls and puts from Step (1). This smoothed
    measure controls for noise and gives us the base
    notional volume imbalance.

(3) We standardise the imbalance measure calculated
    from Step (2) by dividing it by its 1-year historical
    volatility. This gives us the signal, $S_t^{\text{COFFEE}}$.⁸³

### 4.5.2 Signal predictive power

> Figure 31 indicates that the COFFEE signal has been
> quite powerful, with MIC levels that are almost as high
> as those in the Carry factor and which are not matched
> by any of our other short-term signals.⁸⁴

> Figure 31: COFFEE signal – modified information
> coefficient
[Figure: A bar chart comparing time-series and cross-sectional modified information coefficients for the COFFEE signal across horizons (1D, 2D, 1W, 1M, 1Y).]

Source: Deutsche Bank

> Figure 32 also confirms its relationship with Momentum.
> The more that calls are favoured over puts, the higher
> the signal value, and the more likely the asset is to rise
> over the next 1 month. It also suggests signal returns
> can be more convex when predicting US dollar
> depreciation.

> Figure 32: COFFEE signal – relationship between signal
> level and future 1-month asset returns
[Figure: A box plot showing the relationship between COFFEE signal level and future 1-month asset returns, with median and percentile ranges.]

Source: Deutsche Bank

### 4.5.3 Weighting schemes: time series and cross-sectional

We apply the same weighting schemes as those from
the Momentum Spill-Over portfolios, thereby focusing
primarily on turnover control and cost reduction. This
also implied under-utilising signal intensity, an
unfortunate side effect given the high MICs shown in
Section 4.5.2.

79 As supporting evidence, Weng and Grover (2017) documented that
volume data on higher delta options correlated more positively with CFTC
futures data associated with non-commercial participants.
80 This may seem like a stronger assumption, but note that the variance
risk premium in foreign exchange is much lower than in other asset
classes. Not only was it backed by randomised internal trade samples, but
also frequently observed in our option surveys as published in the DB
Global FX Gamma Reports since 2008 (see, for instance, Natividade
(2008)).

81 While CNH was in the original pool, we removed it from this research
paper as it is not part of the other signals.
82 And not expiring at the date of signal evaluation, i.e. non-expiring
options.
83 The COFFEE signals are available on Bloomberg.
84 While it doesn't reduce its value-add, one could argue the high MICs are
due to its short-term history and less straight forward access. For a review
of the typical life cycle of a new signal, see Ilmanen (2011).

Page 24
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

At a given rebalancing date, the weight allocated to a
given asset in the time series COFFEE portfolio is
calculated as follows:

$$
w_i = \text{sign}(S_t^{\text{COFFEE}}) \times \frac{1/\tilde{\sigma}_{r_i}}{\sum_{j=1}^N 1/\tilde{\sigma}_{r_j}}
$$

As for the cross-sectional COFFEE portfolio, the asset
weights are calculated using the following steps:

(1) We rank currency pairs based on the signals
    estimated in Section 4.5.1.

(2) We go long the top half and short the bottom half of
    assets in our pool, assigning equal weights to each
    asset such that the absolute sum of weights equals
    100%. We opt for taking exposure to all assets so as
    to maximise factor exposure and avoid idiosyncratic
    risk.

(3) We re-adjust the weights from Step (2) such that the
    net beta to the US dollar is zero:

$$
\arg \min_w \sum (w_i - \tilde{w}_i)^2, \text{ such that } \sum w_i \beta_i = 0
$$

In this case, $\tilde{w}_i$ is the initial USD/FX weight and $\beta_i$
represents the currency beta to the USD.⁸⁵

Note that we keep the asset and portfolio boundary
constraints as before in both time series and cross-
sectional constructs.

### 4.5.4 Portfolio tranching

We opted for weekly rebalancing, with daily tranching,
as in line with our Momentum spill-over portfolios.
Figure 33 suggests that a slightly faster rebalance would
lead to higher risk-adjusted returns, but not enough to
compensate for the turnover pick-up.

### 4.5.5 Backtest results

As with prior factor portfolios, Figure 34 suggests that
the COFFEE time series and cross-sectional portfolios
complement one another. But perhaps more important
is the fact that the time series factor portfolio has been
primarily long USD for much of the backtest period.
Figure 35 shows the weighted average COFFEE signal
over time; given that asset weights only account for
signal sign (and not size) it is no wonder that the time
series portfolio has been heavily correlated to the PC1 of
the asset class⁸⁶.

> Figure 33: Tranching results (time series followed by
> cross-sectional constructs) – COFFEE portfolio
[Figure: Two bar charts showing Sharpe (w/o cost) and Sharpe (w/ cost) and Daily effective T/O (rhs) for COFFEE portfolios across rebalancing frequencies (1D, 2D, 1W, 1M), for both time series and cross-sectional constructs.]

Source: Deutsche Bank

> Figure 34: Time series and market neutral COFFEE
> backtested returns (net of transaction costs)
[Figure: A line chart showing the backtested returns of time-series (SR: 0.75) and cross-sectional (SR: 0.52) COFFEE strategies over time.]

Source: Deutsche Bank

85 Another alternative for beta neutralization involves estimating the USD-
beta of both long and short baskets separately and using these as hedge

ratios. This approach would however require originally allocating equal risk
weights for each asset as opposed to equal USD weights.
86 We note that adjusting positions for signal intensity would have led
portfolio turnover to double.

Page 25
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

> Figure 35: Weighted US dollar COFFEE signal
[Figure: A line chart showing the weighted US dollar COFFEE signal over time from Mar 2014 to Sep 2018.]

Source: Deutsche Bank

> Figure 36: Return correlations to the US dollar, 1Y
> rolling
[Figure: A line chart showing rolling 1-year correlations to the US dollar for time-series and cross-sectional COFFEE strategies.]

Source: Deutsche Bank

## 4.6 Positioning factors: CFTC

Staying within the context of market positioning, our
final short-term signal is based on open interest data on
exchange-traded currency futures contracts as recorded
by the Commodity Futures Trading Commission (CFTC).
The motivation comes from studies suggesting that
CFTC data is a good proxy for the investor community
as a whole, and therefore potentially useful in price
prediction.⁸⁷

We start with 2 behavioural-based priors:

*   First order dynamics – i.e. net positioning – by non-
    commercial participants point towards price
    momentum, reflecting the likelihood that this class of
    market participants are trend followers.
*   Second order dynamics – in other words, changes in
    these positions – point towards price reversal. This
    reflects the likelihood that abnormally high flows lead
    to overshoot and subsequent retracement in asset
    prices.

Testing these priors can be challenging due to how
CFTC data is made publicly available. Weekly
Commitment of Traders (COT) reports⁸⁸ are released on
Friday at 15:30 EST with information related to prior
Tuesday's close. Conservative backtesting therefore
assumes the signal is executed the following Monday, a
delay of 4 business days. Further, the low frequency
with which the data is made available - one weekly
snapshot - also introduces discretisation error. The two
shortcomings are especially detrimental to signals that
decay fast, as is arguably the case with short-term
reversals - our second prior above.

As is the case with the COFFEE signal, our CFTC signals
are applied to a subset of the original pool of assets, due
to data availability. The assets are: EUR/USD, AUD/USD,
GBP/USD, USD/CAD, USD/JPY, NZD/USD, USD/CHF,
USD/BRL, USD/MXN and USD/RUB.

### 4.6.1 Signal generation

We create 2 signals from the CFTC data: a continuation
and a reversal signal. Both are calculated once a week,
as the COT data is made available.

The continuation signal for a given asset is calculated as
follows:

$$
S_{i,t}^{\text{NC}} = \sum_{h=0}^3 I_{i,t-h}^{\text{NC}}
$$

$$
S_{i,t}^{\text{CFTC,C}} = \frac{S_{i,t}^{\text{NC}} - S_{i,t}^{\text{SNC}}}{S_{i,t}^{\text{LNC}} + S_{i,t}^{\text{SNC}}}
$$

where $I_{i,t}^{\text{NC}}$ represents long positions for week $t$ from
non-commercial traders, sometimes known as "large
speculators", and $S_{i,t}^{\text{SNC}}$ represents short positions from
the non-commercial traders. Note that we apply a
4-week sum as noise control measure, just as is the case
in the COFFEE signal introduced earlier.

87 Upperman (2006), in his book, discussed various ways to understand
and use COT data through different trading strategies. Sanders et al. (2006)
investigated the forecasting ability of CFTC's Commitments of Traders
data. He found that traders' positions do not show a systematic tendency
to lead returns and the positions follow returns. Wang (2003) found that
over intervals from one to twelve weeks, that non-commercial traders'
positions forecast price continuations and commercial traders forecast
price reversals.

88 The report provides a breakdown of aggregate positions held by three
different types of traders: "commercial traders," "non-commercial
traders" and "non-reportable." "Commercial traders" are sometimes
called "hedgers", "non-commercial traders" are sometimes known as
"large speculators," and the "non-reportable" group is sometimes called
"small speculators".

Page 26
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

The reversal signal for asset $i$ is calculated using the
following steps:

(1) Calculate the z-score of the current net position
    ($I_{i,t}^{\text{NC}} - S_{i,t}^{\text{SNC}}$ above) for the asset, using 3 lookback
    windows for z-score estimation: 1, 2 and 3 months.

(2) Calculate the average of the 3 z-scores from Step (1).

(3) Calculate the volatility of daily asset returns over the
    past 6 months. The final signal, $S_i^{\text{CFTC,R}}$, is the ratio of
    the average z-score from Step (2) over asset volatility,
    multiplied by -1 so as to represent reversal and not
    continuation. We apply no noise control to this signal
    so as to preserve its speed.

### 4.6.2 Signal predictive power

As with all other cases, we estimated modified
information coefficients introduced in Section 3 for the
CFTC signals above. The MICs reiterate our priors: the
first signal points to continuation, or momentum, and
the second to reversals. Three other observations are
worth noting:

*   The time series version of the reversal signal does not
    exhibit any predictive power. It highlights that this
    reversal factor should be captured as a relative
    phenomenon. This is shown in Figure 38.

*   The cross-sectional version also shows a clear
    difference in speed: the reversal signal is faster while
    the continuation signal is slower. This is shown in
    Figure 39.

*   Its slower nature favours the continuation signal, as
    it becomes less vulnerable to discretisation error and
    reporting lag. We also note that its MIC values are
    higher than what we found in the price action
    momentum signal, which reiterates our argument
    that price action signals coming from alternative
    market data may at times be better than those
    coming from price action data. A comparison
    between Figure 37 with Figure 9 also highlights this
    point.

> Figure 37: CFTC continuation signal - modified
> information coefficient
[Figure: A bar chart comparing time-series and cross-sectional modified information coefficients for the CFTC continuation signal across horizons (1W, 2W, 1M, 3M, 1Y).]

Source: Deutsche Bank

> Figure 38: CFTC reversal signal - modified information
> coefficient
[Figure: A bar chart comparing time-series and cross-sectional modified information coefficients for the CFTC reversal signal across horizons (1W, 2W, 4W, 3M, 1Y).]

Source: Deutsche Bank

> Figure 39: MICs for cross-sectional versions of the
> CFTC continuation and reversal signals
[Figure: A bar chart comparing cross-sectional MICs for CFTC Reversal and Continuation signals across horizons (1W, 2W, 4W, 3M, 1Y).]

Source: Deutsche Bank

### 4.6.3 Weighting schemes: time series and cross-sectional

Page 27
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

The weighting schemes used in our CFTC continuation
signals are the same as those applied in other short-term
signals: inverse volatility weights for the time series
implementation, and equal notional weights, with a
target beta to the USD, in the cross-sectional version.

With regards to the CFTC reversal signal, however, we
remove the time series construct - Section 4.6.2 shows
it lacks predictive power – and remove the beta target
constraint from the cross-sectional construct, as the
unconstrained version has already been historically
market neutral.

The weighting scheme for our time series continuation
signal is calculated as follows:

$$
w_i = \text{sign}(S_i^{\text{CFTC,C}}) \times \frac{1/\tilde{\sigma}_{r_i}}{\sum_{j=1}^N 1/\tilde{\sigma}_{r_j}}
$$

The weighting scheme for the cross-sectional CFTC
signals is calculated as follows:

(1) We rank currency pairs based on the signals
    estimated in Section 4.6.1.

(2) We go long the top half and short the bottom half of
    assets in our pool, assigning equal weights to each
    asset such that the absolute sum of weights equals
    100%. We opt for taking exposure to all assets so as
    to maximise factor exposure and avoid idiosyncratic
    risk.

(3) Specifically in the case of the CFTC continuation
    portfolio, we re-adjust the weights from Step (2) such
    that the net beta to the US dollar is zero:

$$
\arg \min_w \sum (w_i - \tilde{w}_i)^2, \text{ such that } \sum w_i \beta_i = 0
$$

In this case, $\tilde{w}_i$ is the initial USD/FX weight and $\beta_i$
represents the currency beta to the USD.⁸⁹

Note that we keep the asset and portfolio boundary
constraints as before in both time series and cross-
sectional constructs.

### 4.6.4 Portfolio tranching

Figure 40 plots the effects of different rebalancing
windows, all tranched weekly, on performance and
turnover for both CFTC signals, using both time series
and cross-sectional implementations.

The rebalancing effects do not look highly significant,
but the fast overall nature of this signal leads us to
favour weekly rebalancing. This keeps it consistent with
our other short-term factor portfolios.

> Figure 40: Tranching results (time series followed by
> cross-sectional constructs) – CFTC continuation
> portfolio
[Figure: Two bar charts showing Sharpe (w/o cost) and Sharpe (w/ cost) and Weekly effective T/O for CFTC continuation portfolios across rebalancing frequencies (1W, 2W, 1M, 3M), for both time series and cross-sectional constructs.]

Source: Deutsche Bank

> Figure 41: Tranching results – CFTC reversal portfolio
[Figure: Two bar charts showing Sharpe (w/o cost) and Sharpe (w/ cost) and Weekly effective T/O for CFTC reversal portfolios across rebalancing frequencies (1W, 2W, 1M, 3M), for both time series and cross-sectional constructs.]

Source: Deutsche Bank

89 Another alternative for beta neutralization involves estimating the USD-
beta of both long and short baskets separately and using these as hedge

ratios. This approach would however require originally allocating equal risk
weights for each asset as opposed to equal USD weights.

Page 28
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

### 4.6.5 Backtest results

Figure 42 shows the backtested results of our 3
qualifying CFTC porttfolios, and Figure 43 shows how
they correlate to the broad US dollar over time.

> Figure 42: Time series and cross-sectional CFTC
> backtested returns (net of transaction costs)
[Figure: A line chart showing the backtested returns of time-series (SR: 0.33), cross-sectional (SR: 0.25), and Reversal (SR: 0.25) CFTC strategies over time.]

Source: Deutsche Bank

> Figure 43: Return correlations to the US dollar, 1Y
> rolling
[Figure: A line chart showing rolling 1-year correlations to the US dollar for time-series, cross-sectional, and Reversal CFTC strategies.]

Source: Deutsche Bank

### 4.6.6 Discretisation risk in the CFTC reversal portfolio

As we highlighted earlier, the fast decay in our cross-
sectional reversal signal raises concerns given that CFTC
data can only be snapped weekly. This rewarded an
extra exercise to evaluate the risk of discretisation errors
in the way the signal is built.

In order to test for this risk, we conducted an exercise
where we randomly bumped the original reversal signal
for each asset (and for each rebalancing date) by a small
fixed quantity, which could be interpreted as sampling
error.⁹⁰ The exercise was repeated for 100 simulated
"backtests", thus providing us with a new distribution of
Sharpe ratios.

> Figure 44: Distribution of Sharpe ratio estimates for
> the CFTC reversal portfolio after 100 simulations with
> bumped signals (bump size = 5 percentile)
[Figure: A histogram showing the distribution of Sharpe ratio estimates for the CFTC reversal portfolio from 100 simulations, with an indication of the Original backtest Sharpe ratio.]

Source: Deutsche Bank

The results of this exercise suggest that we cannot
ignore the risk of discretisation error. After accounting
for costs, the interquartile range of the distribution of
Sharpe ratios sits at 0.19-0.21, and the backtested
Sharpe ratio using the original signals is at 0.22 (85th
percentile). If we change the bump assumptions to a
slightly wider random number⁹¹, the interquartile range
becomes 0.15-0.21 and the backtested Sharpe ratio
moves to the 78th percentile. In other words, slight
changes in our estimate of market positioning - which
can occur as we snap the data at a low frequency - may
have meaningful effects on our factor portfolio. As such,
we suggest exercising caution when allocating capital
to this particular reversal signal.

90 Equal to the 1st percentile of the distribution of absolute signal levels.

91 5th percentile instead of the 1st percentile. Note that we also applied the
same exercise in the cross-sectional CFTC momentum signal as a check,
and the results suggest there is far less discretisation risk in that case.

Page 29
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

# 5. Currency Risk Management

Managing currency risk is of key interest to cross-border
investors. Poor management can negate a large portion
of the gains from diversifying into a portfolio of foreign
assets.

In addition, the immediate alternative - cancelling out
currency risk through forward contracts - can be sub-
optimal. It may not only remove economic gains, but
also increase the risk in the total portfolio.

A good example is that of the Australia-based investor
who buys Japanese equities and is therefore short
AUD/JPY. The negative correlation between FX and
equity exposures makes it such that being un-hedged is
more risk-reducing to the combined position than
neutralizing FX risk through AUD/JPY forwards. A sell-
off in Japanese equities typically coincides with a
weaker AUD (versus the JPY), and the natural short
AUD/JPY position, if un-hedged, cushions the losses
coming from Japanese equities. As such, being un-
hedged would have offered a better risk profile.

This section outlines our new Informed Dynamic
Currency Hedging (IDCH) framework. The hedging
decisions are based on the following flow process:

> Figure 45: Hedging flow process
[Figure: A flowchart illustrating the Informed Dynamic Currency Hedging (IDCH) process, starting from an investor buying foreign assets, evaluating foreign currency appreciation likelihood, and deciding whether to hedge.]

Source: Deutsche Bank

Currency hedging has also received significant
treatment in both academic and industry literature, of
which we reference Campbell et al (2009), Brown and
Zhang (2012), Brehon (2013), Chen et al (2013),
Saravelos and Harvey (2013), Karolyi and Wu (2017),
Bucher (2017), Opie et al (2018). There are 3 steps to our
IDCH framework: risk estimation, return estimation, and
hedge ratio estimation. The first part was outlined in
Section 1.2, and hence we focus on the latter 2.

### 5.1 Return estimation

Predicting whether a foreign currency is likely to rise or
fall should be an integral part of the FX hedging exercise
- the more likely it is to rise, the less likely one is to
hedge a (long) exposure to it. Keeping in line with that
thought, we use the investment factors from Section 4
as our predictors. But in order to ensure all currency
pairs in the original pool are covered, we also focus on
a smaller set: Momentum Spill-Over, Carry and

Page 30
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

Momentum, and Value. These cover short, medium and
long-term horizons respectively.

In each case, we take the weights built using the time
series construct to define each factor's directional view
on a given currency. We use, therefore, the weights
defined in Section 4.4.3 for the Momentum Spill-Over
factor, Section 4.1.4 for the Momentum factor, Section
4.2.3 for the Carry factor and Section 4.3.3 for the Value
factor.

We opt for the time series weights so that their sign
directly reflects the sign of the respective signals. In
other words, we do not force long-short weights as is
typical of cross-sectional strategies. This is in order to
avoid positions that go against the direction of the
original signal. If we expect all foreign currencies to
appreciate against the USD, for instance, we should not
hedge any of those exposures, as opposed to having half
of them un-hedged (those that we are most bullish) and
half hedged (those that we are least bullish).

Having defined our input factors, the preliminary
currency weight at a given rebalancing date is the
simple average of the individual factor weights:

$$
W_i^{\text{Prelim}} = \frac{1}{Q} \sum_{q=1}^Q W_{i,q}
$$

where $Q = 4$ is the number of weights applicable to
currency $i$.

### 5.2 Estimating hedge ratios

Having defined our risk and return estimates, we are
now ready to define our hedge ratios; in other words,
the weights defining how much the investor should go
short each foreign currency in order to hedge the long
exposure naturally incurred when she bought equities
from those countries.

Note that we do not apply leverage in the methods
introduced here. In other words, the investor cannot go
long the foreign currency in the FX hedge portfolio – she
is already long FX in the equities portfolio. Further, the
size of the short position cannot exceed the size of the
respective long exposure from the equities portfolio.

We present 4 methods, which vary according to
complexity. The first 2 methods build hedge ratios on a
currency-by-currency basis, therefore not accounting
for the interactions between currencies - and between
currencies and equities in the portfolio. The final 2
methods apply a basket approach, thereby evaluating all
joint risk exposures before deciding on the final hedge
portfolio. The first 2 methods tend to be in line with the
thought process of corporate hedgers, while the latter 2
tend to be more popular with institutional investors.

### 5.2.1 Method 1: sign-weighted IDCH

The first method is the simplest, as it focuses only on
the sign (and not the size) of the individual factor
weights.

This method has 2 variations, or "schemes": the
proportional hedge ratio and the aggregate hedge ratio.
The first assesses the proportion of the bearish signals
to the total number of signals, while the second
calculates the sum of the signs of all signals.

In other words, the first scheme is as follows:

$$
w_i^H = \frac{1}{Q} \sum_{q=1}^Q \mathbb{1}_{\{W_i^{(q)} < 0\}}
$$

The second scheme is as follows:

$$
w_i^H =
\begin{cases}
1 & \text{if } \frac{1}{Q} \sum_{q=1}^Q \text{sign}(W_i^{(q)}) < 0 \\
0 & \text{otherwise}
\end{cases}
$$

The first scheme is more conservative as the investor
stays hedged most of the time, at varying quantities,
while the second approach is more aggressive.

### 5.2.2 Method 2: size-weighted IDCH

The second method accounts for factor size; in other
words, it also evaluates how much each factor favours
a particular foreign currency. This methods has an
element of "relativity" to it, as each factor allocates a
finite amount of capital across currencies depending on
which ones it favours. That said, the hedge ratios are still
calculated on a currency-by-currency basis.

As before, we introduce 2 schemes. The first scheme is
calculated as follows:

$$
w_i^H = \frac{1}{Q} \sum_{q=1}^Q \mathbb{1}_{\{W_i^{(q)} < 0\}} \times W_i^{(q)}
$$

The second scheme is calculated as follows:

$$
w_i^H =
\begin{cases}
1 & \text{if } \frac{1}{Q} \sum_{q=1}^Q W_i^{(q)} < 0 \\
0 & \text{otherwise}
\end{cases}
$$

### 5.2.3 Methods 3 and 4: size-weighted FX-only IDCH and
### full IDCH

Method 3 builds from the earlier methods in that not
only it takes information from our investment factors,
but it also evaluate the co-movements between the
currencies that need hedging. It can be applied to
corporations with multi-national currency exposure.

Method 4 goes a step further and adds the relationship
between the pool of currencies and the portfolio of
assets that the market participant may be exposed to,
thereby being applicable to international equity and
fixed income portfolio investors. The steps to both
methods follow below.

Page 31
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

We define $S_{i,t}$ as the USD price per unit of foreign
currency $i$ at time $t$, and $P_{i,t}$ as the price of the asset
(including dividends) in the foreign currency $i$ at time $t$.

The unhedged return on that foreign investment
measured from time $t-1$ to $t$ is given by:

$$
r_{i,t}^{\text{uh}} = \frac{P_{i,t} \times S_{i,t}}{P_{i,t-1} \times S_{i,t-1}} - 1
$$

or

$$
r_{i,t}^{\text{uh}} = (1+r_{i,t}^{\text{local}})(1+r_{i,t}^{\text{FX}}) - 1
$$

where $r_{i,t}^{\text{local}}$ and $r_{i,t}^{\text{FX}}$ are one-period returns on the foreign
asset (in local currency) and the currency spot
(expressed in USD per unit of foreign currency – in other
words, FX/USD).

For case 3, we ignore asset returns, so the unhedged
return is simply the currency return: $r_{i,t}^{\text{uh}} = r_{i,t}^{\text{FX}}$.

The one-period return on a long FX forward contract
expressed as a function of the current spot exchange
rate is defined as:

$$
f_{i,t} = \frac{S_{i,t} - F_{i,t-1}}{S_{i,t-1}}
$$

where $F_{i,t}$ denotes the one-period forward dollar price of
foreign currency $i$.

The hedged return on investment in country $i$ is
therefore given by:

$$
r_{i,t}^h = r_{i,t}^{\text{uh}} - h_{i,t} f_{i,t}
$$

where $h_{i,t}$ is the hedge ratio of the investment in country
$i$ at time $t$. We define $h_{i,t} \in [0,1]$, therefore allowing each
foreign currency exposure to be hedged up to 100%. The
investor invests in N+1 assets, where "+1" represents
the domestic (USD-denominated) asset, and is exposed
to N foreign currencies with the USD as base currency.

Let $R_t = [r_{1,t}^{\text{uh}}, r_{2,t}^{\text{uh}}, ..., r_{N,t}^{\text{uh}}, r_{N+1,t}^{\text{uh}}]'$ be an (N+1) x 1
vector of unhedged returns in USD from all countries,
with $r_{N+1,t}^{\text{uh}}$ being the return from the domestic (USD-
denominated) asset.

$W_t$ denotes an (N+1) x 1 vector of portfolio weights $W_{i,t}$
with $W_{N+1,t}$ being the weight allocated to the domestic
asset. These correspond to the weights defined in Table
1, and in this context they vary according to the
frequency that MSCI weights rebalance.

$f$ denotes an N x 1 vector of forward currency returns
$f_{i,t}$, and $h$ is an N x 1 vector of hedge ratios $h_{i,t}$. The
hedged gross portfolio return is given by:

$$
R_t^h = W_t' R_t - h_t'(W_t \circ f_t)
$$

In other words,

$$
R_t^h = (W_t' R_t - w_h' f_t)
$$

where $W$ is an $N \times 1$ vector of portfolio weights $w_i$
excluding the weight of the US and $\circ$ represents
element-by-element multiplication. $W_h$ is an $N \times 1$
vector of hedge positions (or hedge weights). These are
the weights we solve for in our optimisation.

Note that the second term is subtracted from the first
term because all hedge positions imply going short the
foreign currency.

Representing the above equation differently,

$$
R_t^h = \left(\sum_{i=1}^{N+1} W_{i,t} \times r_{i,t}^{\text{uh}}\right) - \left(\sum_{i=1}^N W_{i,h} \times f_{i,t}\right)
$$

In order to estimate the optimal hedge ratio, we solve
for $W_h$ to maximise the following objective function:

$$
\arg \max_{W_h} \frac{W_h' W^{\text{Prelim}}}{\sigma_{R^h}}
$$

or, put differently,

$$
\arg \max_{W_h} \frac{\sum_{i=1}^N W_{i,h} \times W_{i,h}^{\text{Prelim}}}{\sigma_{R^h}}
$$

such that:

$$
W_{i,h} \le (1 - W_{N+1,t})
$$

Finally, we also add a constraint⁹² so that we do not
hedge exposure to a foreign currency if that currency is
expected to appreciate against the base currency (USD
in the present case). In other words:

$$
W_{i,h} =
\begin{cases}
[0, W_{i,t}] & W_i^{\text{Prelim}} > 0 \\
[0, W_{i,t}] & W_i^{\text{Prelim}} \le 0
\end{cases}
$$

### 5.3 Results

We now document the results of various IDCH methods.
Our baseline participant is an equity market investor
long international equities with exposures equivalent to
those of the MSCI World, as standardised in Table 46⁹³.
We start with the assumption that the investor is US-
domiciled, and later also show results assuming the

92 This constraint assumes full "alpha risk"; in other words, we do not
differentiate between strong and moderate positive weights on the foreign
currency. This condition, however, can be relaxed. One way is to modify
the condition according to weight intensity thresholds. Another way would
be to change the hedge ratio at the outside. An example of the latter could

be that if the combined signals favour a currency then we allow to hedge
that currency between 0 and 50%. Otherwise, if combined signals dislike a
currency then we look for a hedge ratio between 50% and 100%.
93 Note that we have removed exposures that are very small.

Page 32
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

investor is based in Europe, Japan and Australia, but
focus exclusively on Method 4.

> Figure 46: MSCI World weights reference table

| Countries       | Weights | Std. weights |
| :-------------- | :------ | :----------- |
| United States   | 50.65%  | 57.01%       |
| Japan           | 7.80%   | 8.78%        |
| United Kingdom  | 5.55%   | 6.25%        |
| France          | 3.41%   | 3.83%        |
| Canada          | 3.22%   | 3.62%        |
| Germany         | 3.21%   | 3.61%        |
| Switzerland     | 3.17%   | 3.56%        |
| Australia       | 2.33%   | 2.62%        |
| South Korea     | 1.80%   | 2.02%        |
| Hong Kong       | 1.55%   | 1.75%        |
| Taiwan          | 1.37%   | 1.55%        |
| Spain           | 1.09%   | 1.22%        |
| Sweden          | 0.97%   | 1.09%        |
| Brazil          | 0.89%   | 1.00%        |
| South Africa    | 0.80%   | 0.90%        |
| Russia          | 0.39%   | 0.44%        |
| Mexico          | 0.38%   | 0.43%        |
| Poland          | 0.16%   | 0.18%        |
| Turkey          | 0.13%   | 0.14%        |
| Total           | 88.85%  | 100.00%      |

Weights current as of Q3 2017. Note that these weights change at every rebalancing date. Source:
Deutsche Bank

In this exercise, we use 1-month forward contracts to
hedge exposure to foreign currencies versus as given
domestic currency. Similar to our approach in earlier
sections, we rebalance our portfolio every month and
apply tranches on a daily basis to reduce sampling error.

We compare our dynamic hedging methods with two
benchmarks:

*   A 100% static hedge: the investor uses 1M forwards
    to fully neutralise her foreign currency exposure; in
    other words, the size of each short position is equal
    to the natural (long) FX exposure in the equities
    portfolio.
*   A 50% static hedge: the investor uses 1M forwards
    to hedge half of her foreign currency exposure. The
    50% hedge is often called a "point of no-regret".

### 5.3.1 US-based investor

> Figure 47 outlines the backtested performance of the
> hedge portfolios in the 4 methods proposed earlier, in
> addition to the two benchmarks.

> Figure 47: Currency hedge portfolio backtests –
> transaction costs included
[Figure: A line chart comparing the performance of different currency hedge portfolio methods (B1, B2, M1_A1, M1_A2, M2_A1, M2_A2, M3, M4) with their respective Sharpe Ratios, from 1991 to 2017.]

Source: Deutsche Bank

These results indicate the following:

*   All IDCH methods outperform the benchmarks in the
    backtest. While the first benchmark hedge fully
    eliminates currency risk from the equities portfolio, it
    also suffers from periods of USD depreciation. The
    second benchmark, which applies a 50% hedge,
    reduces part of that underperformance.

*   The more conservative alternative in our first IDCH
    method tracks the benchmarks more closely, given
    that it has less room to manoeuvre.

*   Other methods outperform, which are more flexible
    and allow for the investor to better capture our
    investment factors and estimate cross-market (and
    cross-asset) risks. Methods that are more complex
    tended to yield better risk-adjusted backtested
    returns.

*   Methods 3 and 4 are highly correlated to the first 2,
    despite also utilising our covariances to better
    manage the risk exposure. This suggests most of the
    value-add comes from the factors introduced in
    Section 4, and that the efficacy of the hedge
    programme depends heavily on that. This is intuitive
    due to the return-seeking nature of our objective
    function. Had we opted for a different utility target,
    the results could have been different.⁹⁴

### 5.3.2 Non-US based investors

We now move onto investors domiciled elsewhere, and
focus on Method 4 for currency hedging. As the reader
would expect, co-movements between the domicile
currency and international equities will lead to distinctly

94 Another potential objective function seeks to minimise total portfolio
variance: $\min_W \text{var}[R_A + R_{\text{FX}}(W)]$, with the same constraints as used earlier.

This approach follows the premise that currency risks are not rewarded,
but can be used to reduce total portfolio volatility and free risk capital that
can be allocated elsewhere.

Page 33
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

different conclusions depending on the country in
question.

Our next investor of interest is Europe-based. Method 4
therefore accounts for how the Euro and global equities
co-vary over time, in addition to utilising our predictive
factors when deciding exposures. The backtests shown
in Figure 48 suggest these would have made a
particularly positive difference in the late 1990s and
early 2000s.

Hedging global equity exposure for the Japan-based
investor is also an important case study, due to the
negative correlation between the JPY and global
equities and the high cost of hedging due to low
domestic interest rates. If unhedged, the Japanese
investor suffers even more from global equity weakness;
if hedged, they suffer from high hedging costs. Figure
48 shows that the IDCH Method 4 would have favoured
being globally unhedged over long periods of time.

Finally, we present backtest results for the Australia-
based investor, whose currency overlay challenges are
often opposite to those of the Japanese investor. Not
only the AUD is positively correlated to global equities,
which cushions losses during risk aversion, but short
AUD/FX positions are cheaper to hedge given the high
domestic interest rates. In this case, Method 4 suggests
hedging a greater proportion of the currency exposures
historically as per high correlation with the first
benchmark method.

# 6. Conclusions

This reports outlined a recipe for systematic investing in
foreign exchange. We started by outlining the common
variations and drivers of the asset class across different
horizons. Once these drivers were understood, we then
created a framework to assess how to optimally attain
exposure for both absolute returns and currency
hedging purposes. All the main implementation aspects
- signal generation, aggregation, rebalancing and risk -
were addressed carefully in each section.

We introduce 7 signals in this report:

*   Rates spill-over momentum, DTCC positioning and
    CFTC positioning (momentum and reversal): these
    cover short-term price action and sentiment
    dynamics.
*   Momentum and Carry: these have better predictive
    power medium-term horizons.
*   Value: covering fundamental currency dynamics and
    whose impact spans over longer horizons.

Most signals are implemented through both time-series
and cross-sectional constructs, therefore distinctly
addressing the drivers of the US dollar and of other
currencies. The two constructs are highly complementary
to one another. Further, in currency hedging, we show 4
methods to achieve optimal currency exposure through
the above factors, with implications to both corporates
and institutional investors.

> Figure 48: IDCH Method 4 currency hedging portfolios
> - Europe, Japan and Australia-based investors
[Figure: Three line charts showing the performance of IDCH Method 4 (M4) compared to benchmarks (B1, B2) for Europe-based, Japan-based, and Australia-based investors, with their respective Sharpe Ratios.]

Source: Deutsche Bank

Page 34
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

# 7. Bibliography

Anand, V., Natividade, C., Mesomeris, S., Davies, C.,
Jian, S., and Capra, J. (2014), Riding Carry, Deutsche
Bank Quantcraft.

Anand, V., Natividade, C., and Mesomeris, S. [2016],
"Protect Your Core", Deutsche Bank Quant Snaps, 07
November 2016.

Anand, V., Natividade, C., Capra, J., Mesomeris, S.,
Moniz, A., Osiol, J., Tentes, A., Ward, P. [2017], "Protect,
Diversify or Track Your Core", Deutsche Bank
Quantcraft, 17 August 2017.

Anand, V., Natividade, C., and Gonzalez, J. (2018),
Modern Portfolio Construction Meets FX: A framework
for absolute return and hedging strategies, Deutsche
Bank Cross Asset Quantitative Research Presentation.

Ang, A. (2014), Asset Management: A Systematic
Approach to Factor Investing, Oxford University Press,
1st Edition.

Ang, A., and Chen, S.J. (2010), Yield curve predictors of
foreign exchange returns, Working Paper, Columbia
University.

Asness, C., Moskowitz, T. and Pedersen, L. (2013), Value
and Momentum Everywhere, The Journal of Finance,
Vol 68, No. 3, June 2013.

Bartram, S. M., Djuranovik, L., and Garratt, A. (2018),
Currency Anomalies. Electronic copy available at
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3
194107

Baz, J., Granger, N., Harvey, C. R., Rouzx, N. L., and
Rattray, S. (2015), Dissecting Investment Strategies in
the Cross Section and Time Series.

Blitz, D. C., Huij, J. J. and Martens, M. P. E. (2011),
Residual Momentum, Journal of Empirical Finance, Vol.
18, Issue 33, p. 506-521.

Brehon, D. (2013), FEER vs. BEER: Battle of the
Valuation Models. Deutsche Bank Exchange Rate
Perspectives, Special Report.

Brehon, D. (2013), Global Asset Allocation and Optimal
Dollar Hedging, Deutsche Bank Special Report.

Brown, C., Dark, J., and Zhang, W. (2012). Dynamic
Currency Hedging for International Stock Portfolios.
Review of futures markets, 20:419-455.

Bucher, M. C. (2017), Dynamic Conditional Currency
Hedging. Electronic copy available at:
https://ssrn.com/abstract=2999463

Burnside, C., Eichenbaum, M. S., and Rebelo, S. (2011),
Carry Trade and Momentum in Currency Markets, NBER
Working Paper Series.

Campbell, J. Y., Medeiros, K. S., and Viceira, L. M. (2009),
Global Currency Hedging, Journal of Finance.

Capra, J., Natividade, C., and Thakkar, K. (2018), Factor
Investing in Corporate Credit, DB Cross Asset
Quantitative & Derivatives Research, January 2018.

Chadha, B. and Nystedt, J. (2006), Fair Value Lines in the
Sand, The Big Picture, Deutsche Bank Exchange Rate
Perspectives.

Chaves, D. (2012), Eureka! A Momentum Strategy that
Also Works in Japan, Working Paper, 9 January 2002.
Available at SSRN:or
http://dx.doi.org/10.2139/ssrn.1982100.

Chen, W., Kritzman, M., and Turkington, D. (2013),
Which Currency Hedging Strategy is Best? MIT Sloan
School Working Paper 5003-13, Electronic copy
available at: http://ssrn.com/abstract=2268559

Chen, Y.C., and Tsang, K.P. (2009), What does the yield
curve tell us about exchange rate predictability?,
Working Paper, University of Washington.

Cheung, Y.W., Menzie, D.C. and Pascual, A.G. (2002),
Empirical Exchange Rate Models of the Nineties: Are
they Fit to Survive?" NBER WP. 9393.

Christiansen, C., Ranaldo, A. and Soderlind, P. (2010),
The Time-Varying Systematic Risk of Carry Trade
Strategies, Swiss National Bank Working Papers, 2010-
1.

Cline, W. R. (2008), Estimating Consistent Fundamental
Equilibrium Exchange Rates, Working Paper Series.
Available at https://piie.com/publications/wp/wp08-
6.pdf.

Dahlquist, M., and Hasseltoft, H. (2016), Economic
Momentum and Currency Returns, Working Paper.

Engle, C.M., and West, K.D. (2005), Exchange Rates and
Fundamentals, Journal of Political Economy, 113- 485-
517.

Engel, C.M., and Hamilton, J.D. (1990), Long swings in
the dollar: Are they in the data and do markets know it?,
American Economic Review 80, 689-713.

Page 35
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

Evans, M. and Lyons, R. (2002), Order flow and
exchange rate dynamics, Journal of Political Economy,
110 (2002), 170-180.

Fama, E. and MacBeth, J. (1973), Risk, Return, and
Equilibrium: Empirical Tests, The Journal of Political
Economy, Vol. 81, No. 3 (May-Jun., 1973), p.607-636.

Georges, N. (2014), ΑΝΑΝTA: A systematic quantitative
FX trading strategy, Working Paper. Available at SSRN.

Giacomelli, D. and Zhang, J. (2016), What drives excess
returns on FX carry?, Deutsche Bank Foreign Exchange
Research, 7 November 2016.

Gonzalez, J., Natividade, C., and Anand, V. (2018),
Factor Investing in Corporate Credit, Deutsche Bank
Cross Asset Quantitative & Derivatives Research
Presentation.

Grinold, R. C., Kahn, R. N. (1999), Active Portfolio
Management, McGraw Hill, 2nd edition.

Gutierrez, R. C. and Pirinsky, C. (2007), Momentum,
reversal, and the trading behaviors of institutions,
Journal of Financial Markets, 10:48-75.

Gutierrez, R. C., and Kelley, E. (2008), The Long-Lasting
Momentum in Weekly Returns, Journal of Finance, vol.
63, no. 1, p.415-447, February 2008.

Haesen, D., Houweling, P., and van Zundert, J. (2017),
Momentum Spillover from Stocks to Corporate Bonds,
January 2017, Working Paper. Available at SSRN.

Hafeez, B. (2007), Currencies: Value Investing, Deutsche
Bank FX Strategy, 29 March 2007.

Harvey, C. and Liu, Y. (2018), Lucky Factors, Working
Papers, 15 January 2018. Available at SSRN:
https://ssrn.com/abstract=2528780 or
http://dx.doi.org/10.2139/ssrn.2528780.

Hassan, T. (2013), Country Size, Currency Unions, and
International Asset Returns, Journal of Finance 68,
2269-2308.

Hassan, T. A., Mano, R. C. (2014), Forward and Spot
Exchange Rates in a Multi-Currency World, NBER
Working Paper Series.

Ilmanen, A. (2011), Expected Returns: An Investor's
Guide to Harvesting Market Rewards, John Wiley &
Sons, 1st Edition.

Jostova, G., Nikolova, S., Philipov, A., and Stahel, C.
(2013), Momentum in Corporate Bond Returns, Review
of Financial Studies, vol. 26, no. 7: 1649-1693.

Jussa, J., Cahan, R., Alvarez, M., Luo, Y., Chen, J., and
Wang, S. (2012), Signal Processing: Cross Asset Class
Momentum, Deutsche Bank Quantitative Strategy.

Kalani, G. (2016), FX Valuations: A framework and an
introduction to our new DBeer model, Deutsche Bank
Special Report.

Karolyi, G. A. and Wu, Y. (2017), Another Look at
Currency Risk in International Stock Returns. Electronic
copy available at: https://ssrn.com/abstract=3056845

Kassam, A., Mesomeris, S., and Salvini, M. (2010),
Portfolios Under Construction: Factor Neutralization and
Beyond, Deutsche Bank Quantitative Strategy, 21
September 2010.

Koijen, R., Moskowitz, T., Pedersen, L., and Vrugt, E.
(2013), Carry, Fama-Miller Working Paper.

Lopez de Prado, M. (2018) Advances in Financial
Machine Learning, Wiley.

Lothian, J. R., and Taylor, M. P. (2000), Purchasing
power parity over two centuries: strengthening the case
for real exchange rate stability: A reply to Cuddington
and Liang, Journal of International Money and Finance,
Elsevier, vol. 19(5), pages 759-764.

Lustig, H., and Verdelhan, A. (2007), The Cross-section
of Foreign Currency Risk Premia and Consumption
Growth Risk, American Economic Review 97, 89-117.

Lustig, H., and Verdelhan, A. (2007), The Cross-section
of Foreign Currency Risk Premia and Consumption
Growth Risk: A Reply, American Economic Review 101,
3477-3500.

Lustig, H., Roussanov, N., and Verdelhan, A. (2011),
Common Risk Factors in Currency Markets, The Review
of Financial Studies, Volume 24, Issue 11, 1 November
2011.

Lustig, H., Roussanov, N., and Verdelhan, A. (2014),
Countercyclical currency risk premia, Journal of
Financial Economics, 111: 527-553.

Maurer, T. A., To, T. D., and Tran, N. K. (2016), Optimal
Factor Strategy in FX Markets. Electronic copy available
at
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2
797483.

Menkhoff, L., Sarno, L., Schmeling, M., and Schrimpf, A.
(2010), Carry Trades and Global Foreign Exchange
Volatility, Working Paper, Available at SSRN.

Page 36
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

Menkhoff, L., Sarno, L., Schmeling, M., and Schrimpf, A.
(2011), Currency Momentum Strategies, BIS Working
Papers No 366, December 2011.

Menkhoff, L., Sarno, L., Schmeling, M., and Schrimpf, A.
(2013), Currency Risk Premia and Macro Fundamentals,
ECB- Bank of Canada Workshop on Exchange Rates,
Frankfurt.

Menkhoff, L., Sarno, L., Schmeling, M., and Schrimpf, A.
(2015), Currency Value, Available at SSRN website
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2
492082

Mesomeris, S., Wang, Y., and Avettand-Fenoel, J. (2012),
Thematic Report- A New Asset Allocation Paradigm,
Deutsche Bank Quantitative Strategy.

Mesomeris, S. (2018), Current Issues and Development
in Risk Premia Investing, Deutsche Bank Global
Quantitative Strategy Presentation.

Moskowitz, T., Ooi, Y., and Pedersen, L. (2011), Time
Series Momentum, Chicago Booth Research Paper No.
12-21.

Mueller, P., Stathopoulos, A., and Vedolin, A. (2013),
International Correlation Risk, Financial Markets Group
Discussion Paper 716, January 2013. Available at
SSSRN.

Natividade, C. (2008), Internal Trader Survey- 25 January
2008, Deutsche Bank Global FX Gamma Report.

Natividade, C., Mesomeris, S., Alvarez, M., Beceren, M.
and Davis, C (2013), "Colours of Trend", Deutsche Bank
Quantcraft, 17 September 2013.

Natividade, C., Mesomeris, S., Davies, C., Jiang, C.,
Capra, J., Anand, V. and Qu, S. (2014), Value Investing:
Tricky But Worthy, Deutsche Bank Quantcraft, 3
December 2014.

Natividade, C., Anand, V. Mesomeris, S., Davies, C.,
Ward, P., Capra, J., Qu, S. and Osiol, J. (2015), Delving
Into New Territories, Deutsche Bank Quantcraft, 10
November 2015.

Natividade, C., Anand, V. Mesomeris, S., (2016), Signal
And Noise, Part 2, Deutsche Bank Quant Snaps.

Natividade, C., and Anand, V. (2016), Trend Following:
Asymmetries and Thresholds, Deutsche Bank Quant
Snaps.

Opie, W. and Riddiough, S. J. (2018), Global Currency
Hedging with Common Risk Factors. Electronic copy
available at: https://ssrn.com/abstract=3264531

Rafferty, B. (2012), Currency Returns, Skewness and
Crash Risk, Job Market Paper, 15 March 2012. Available
at SSRN.

Raza, A., Marshall, B., and Visaltanachoti, N. (2013), Is
There Momentum or Reversal in Weekly Currency
Returns?, 22 April 2013, Working Paper. Available at
SSRN.

Ricci, L. A., Messi-Ferretti, G. M., Lee, J. (2008), Real
Exchange Rates and Fundamentals: A Cross-Country
Perspective, IMF Working Paper.

Riddiough, S. (2014), The Mystery of Currency Betas,
Working Paper, Warwick Business School.

Rogoff, K. (1996), The Purchasing Power Parity Puzzle,
Journal of Economic Literature, 34, 647-668.

Rosenberg, M. (2002), The Deutsche Bank Guide to
Exchange-Rate Determination: A Survey of Exchange-
Rate Forecasting Models and Strategies, Deutsche Bank
Global Markets Research, May 2002.

Rosenberg, M. (2013), The Carry Trade: Theory, Strategy
and Risk Management, Bloomberg.

Sarno, L., and Schmeling, M. (2013), Which
Fundamentals Drive Exchange Rates? A Cross-Sectional
Perspective, Working Paper. Available at SSRN:
https://ssrn.com/abstract=1835747 or
http://dx.doi.org/10.2139/ssrn.1835747.

Saravelos, G. and Harvey, O. (2013), Introducing the
Corporate Hedging Monitor, Deutsche Bank FX Special
Reports.

Saravelos, G., Gopal, S., Grover, R., Natividade, C.,
Harvey, O., Anand, V., Winkler, R., and Kalani, G. (2018),
Alive and Kicking: A Guide to FX as an Asset Class,
Deutsche Bank Foreign Exchange Research, 2 May 2018.

Serban, A. F., (2010), Combining Mean Reversion and
Momentum Trading Strategies in Foreign Exchange
Markets, Journal of Banking and Finance 34, 2720-2727.

Upperman, F. (2006), Commitments of Traders:
Strategies for Tracking the Market and Trading
Profitably. John Wiley & Sons, New Jersey.

Varadi, D., Kapler, and M., Bee, H. (2012), The Minimum
Correlation Algorithm: A Practical Diversification Tool,
Corey Rittenhouse, September 2012.

Vederlhan, A. (2012), The Share of Systematic Variation
in Bilateral Exchange Rates, USC FBE Finance Seminar.
Available at SSRN.

Page 37
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

Vederlhan, A. (2015), The Share of Systematic Variation
in Bilateral Exchange Rates, Journal of Finance,
Forthcoming. Available at SSRN.

Vederlhan, A. (2018), The Share of Systematic Variation
in Bilateral Exchange Rates, Journal of Finance 73: 375-
418.

Wang, C., (2003), The Behavior and Performance of
Major Types of Futures Traders, Journal of Futures
Markets, 23(2003):1-31.

Weng, N. (2017), A Behavioural Approach to Event
Forecasting- Introducing the Persona Model, Deutsche
Bank Special Report.

Weng, N. and Grover, R. (2017), Options Flows Matter:
Introducing the Deutsche Bank Skew Volume
Indicators, Deutsche Bank Special Report.

Winkler, R. (2017), Where Value Works in FX, Deutsche
Bank Special Report.

Zorzi, M. C., and Rubaszek, M. (2018), Exchange Rate
Forecasting on a Napkin, Working Paper Series,
European Central Bank.

Page 38
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

# Appendix 1

# Important Disclosures

### Additional information available upon request

Prices are current as of the end of the previous trading session unless otherwise indicated and are sourced from local
exchanges via Reuters, Bloomberg and other vendors. Other information is sourced from Deutsche Bank, subject
companies, and other sources. For disclosures pertaining to recommendations or estimates made on securities other
than the primary subject of this research, please see the most recently published company report or visit our global
disclosure look-up page on our website at https://research.db.com/Research/Disclosures/CompanySearch. Aside from
this report, important conflict disclosures can also be found at
https://research.db.com/Research/Topics/Equities?topicId=RB0002 under the "Disclosures Lookup" and "Legal" tabs.
Investors are strongly encouraged to review this information before investing.

# Analyst Certification

The views expressed in this report accurately reflect the personal views of the undersigned lead analyst(s). In addition, the
undersigned lead analyst(s) has not and will not receive any compensation for providing a specific recommendation or
view in this report. Vivek Anand/Caio Natividade/George Saravelos/Jose Gonzalez/Shreyas Gopal/Rohini Grover

# Hypothetical Disclaimer

Backtested, hypothetical or simulated performance results have inherent limitations. Unlike an actual performance record
based on trading actual client portfolios, simulated results are achieved by means of the retroactive application of a
backtested model itself designed with the benefit of hindsight. Taking into account historical events the backtesting of
performance also differs from actual account performance because an actual investment strategy may be adjusted any
time, for any reason, including a response to material, economic or market factors. The backtested performance includes
hypothetical results that do not reflect the reinvestment of dividends and other earnings or the deduction of advisory
fees, brokerage or other commissions, and any other expenses that a client would have paid or actually paid. No
representation is made that any trading strategy or account will or is likely to achieve profits or losses similar to those
shown. Alternative modeling techniques or assumptions might produce significantly different results and prove to be
more appropriate. Past hypothetical backtest results are neither an indicator nor guarantee of future returns. Actual
results will vary, perhaps materially, from the analysis.

Page 39
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

# Additional Information

The information and opinions in this report were prepared by Deutsche Bank AG or one of its affiliates (collectively
"Deutsche Bank"). Though the information herein is believed to be reliable and has been obtained from public sources
believed to be reliable, Deutsche Bank makes no representation as to its accuracy or completeness. Hyperlinks to third-
party websites in this report are provided for reader convenience only. Deutsche Bank neither endorses the content nor
is responsible for the accuracy or security controls of those websites.

If you use the services of Deutsche Bank in connection with a purchase or sale of a security that is discussed in this
report, or is included or discussed in another communication (oral or written) from a Deutsche Bank analyst, Deutsche
Bank may act as principal for its own account or as agent for another person.

Deutsche Bank may consider this report in deciding to trade as principal. It may also engage in transactions, for its own
account or with customers, in a manner inconsistent with the views taken in this research report. Others within Deutsche
Bank, including strategists, sales staff and other analysts, may take views that are inconsistent with those taken in this
research report. Deutsche Bank issues a variety of research products, including fundamental analysis, equity-linked
analysis, quantitative analysis and trade ideas. Recommendations contained in one type of communication may differ
from recommendations contained in others, whether as a result of differing time horizons, methodologies, perspectives
or otherwise. Deutsche Bank and/or its affiliates may also be holding debt or equity securities of the issuers it writes on.
Analysts are paid in part based on the profitability of Deutsche Bank AG and its affiliates, which includes investment
banking, trading and principal trading revenues.

Opinions, estimates and projections constitute the current judgment of the author as of the date of this report. They do
not necessarily reflect the opinions of Deutsche Bank and are subject to change without notice. Deutsche Bank provides
liquidity for buyers and sellers of securities issued by the companies it covers. Deutsche Bank research analysts
sometimes have shorter-term trade ideas that may be inconsistent with Deutsche Bank's existing longer-term ratings.
Some trade ideas for equities are listed as Catalyst Calls on the Research Website (https://research.db.com/Research/),
and can be found on the general coverage list and also on the covered company's page. A Catalyst Call represents a
high-conviction belief by an analyst that a stock will outperform or underperform the market and/or a specified sector
over a time frame of no less than two weeks and no more than three months. In addition to Catalyst Calls, analysts may
occasionally discuss with our clients, and with Deutsche Bank salespersons and traders, trading strategies or ideas that
reference catalysts or events that may have a near-term or medium-term impact on the market price of the securities
discussed in this report, which impact may be directionally counter to the analysts' current 12-month view of total return
or investment return as described herein. Deutsche Bank has no obligation to update, modify or amend this report or to
otherwise notify a recipient thereof if an opinion, forecast or estimate changes or becomes inaccurate. Coverage and the
frequency of changes in market conditions and in both general and company-specific economic prospects make it
difficult to update research at defined intervals. Updates are at the sole discretion of the coverage analyst or of the
Research Department Management, and the majority of reports are published at irregular intervals. This report is provided
for informational purposes only and does not take into account the particular investment objectives, financial situations,
or needs of individual clients. It is not an offer or a solicitation of an offer to buy or sell any financial instruments or to
participate in any particular trading strategy. Target prices are inherently imprecise and a product of the analyst's
judgment. The financial instruments discussed in this report may not be suitable for all investors, and investors must
make their own informed investment decisions. Prices and availability of financial instruments are subject to change
without notice, and investment transactions can lead to losses as a result of price fluctuations and other factors. If a
financial instrument is denominated in a currency other than an investor's currency, a change in exchange rates may
adversely affect the investment. Past performance is not necessarily indicative of future results. Performance calculations
exclude transaction costs, unless otherwise indicated. Unless otherwise indicated, prices are current as of the end of the
previous trading session and are sourced from local exchanges via Reuters, Bloomberg and other vendors. Data is also
sourced from Deutsche Bank, subject companies, and other parties.

The Deutsche Bank Research Department is independent of other business divisions of the Bank. Details regarding our
organizational arrangements and information barriers we have to prevent and avoid conflicts of interest with respect to
our research are available on our website (https://research.db.com/Research/) under Disclaimer.

Page 40
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

Macroeconomic fluctuations often account for most of the risks associated with exposures to instruments that promise
to pay fixed or variable interest rates. For an investor who is long fixed-rate instruments (thus receiving these cash flows),
increases in interest rates naturally lift the discount factors applied to the expected cash flows and thus cause a loss. The
longer the maturity of a certain cash flow and the higher the move in the discount factor, the higher will be the loss.
Upside surprises in inflation, fiscal funding needs, and FX depreciation rates are among the most common adverse
macroeconomic shocks to receivers. But counterparty exposure, issuer creditworthiness, client segmentation, regulation
(including changes in assets holding limits for different types of investors), changes in tax policies, currency convertibility
(which may constrain currency conversion, repatriation of profits and/or liquidation of positions), and settlement issues
related to local clearing houses are also important risk factors. The sensitivity of fixed-income instruments to
macroeconomic shocks may be mitigated by indexing the contracted cash flows to inflation, to FX depreciation, or to
specified interest rates – these are common in emerging markets. The index fixings may - by construction - lag or mis-
measure the actual move in the underlying variables they are intended to track. The choice of the proper fixing (or metric)
is particularly important in swaps markets, where floating coupon rates (i.e., coupons indexed to a typically short-dated
interest rate reference index) are exchanged for fixed coupons. Funding in a currency that differs from the currency in
which coupons are denominated carries FX risk. Options on swaps (swaptions) the risks typical to options in addition to
the risks related to rates movements.

Derivative transactions involve numerous risks including market, counterparty default and illiquidity risk. The
appropriateness of these products for use by investors depends on the investors' own circumstances, including their tax
position, their regulatory environment and the nature of their other assets and liabilities; as such, investors should take
expert legal and financial advice before entering into any transaction similar to or inspired by the contents of this
publication. The risk of loss in futures trading and options, foreign or domestic, can be substantial. As a result of the high
degree of leverage obtainable in futures and options trading, losses may be incurred that are greater than the amount of
funds initially deposited - up to theoretically unlimited losses. Trading in options involves risk and is not suitable for all
investors. Prior to buying or selling an option, investors must review the "Characteristics and Risks of Standardized
Options", at http://www.optionsclearing.com/about/publications/character-risks.jsp. If you are unable to access the
website, please contact your Deutsche Bank representative for a copy of this important document.

Participants in foreign exchange transactions may incur risks arising from several factors, including the following: (i)
exchange rates can be volatile and are subject to large fluctuations; (ii) the value of currencies may be affected by
numerous market factors, including world and national economic, political and regulatory events, events in equity and
debt markets and changes in interest rates; and (iii) currencies may be subject to devaluation or government-imposed
exchange controls, which could affect the value of the currency. Investors in securities such as ADRs, whose values are
affected by the currency of an underlying security, effectively assume currency risk.

Unless governing law provides otherwise, all transactions should be executed through the Deutsche Bank entity in the
investor's home jurisdiction. Aside from within this report, important conflict disclosures can also be found at
https://research.db.com/Research/ on each company's research page. Investors are strongly encouraged to review this
information before investing.

Deutsche Bank (which includes Deutsche Bank AG, its branches and affiliated companies) is not acting as a financial
adviser, consultant or fiduciary to you or any of your agents (collectively, "You" or "Your") with respect to any information
provided in this report. Deutsche Bank does not provide investment, legal, tax or accounting advice, Deutsche Bank is
not acting as your impartial adviser, and does not express any opinion or recommendation whatsoever as to any
strategies, products or any other information presented in the materials. Information contained herein is being provided
solely on the basis that the recipient will make an independent assessment of the merits of any investment decision, and
it does not constitute a recommendation of, or express an opinion on, any product or service or any trading strategy.

The information presented is general in nature and is not directed to retirement accounts or any specific person or account
type, and is therefore provided to You on the express basis that it is not advice, and You may not rely upon it in making
Your decision. The information we provide is being directed only to persons we believe to be financially sophisticated,
who are capable of evaluating investment risks independently, both in general and with regard to particular transactions
and investment strategies, and who understand that Deutsche Bank has financial interests in the offering of its products

Page 41
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

and services. If this is not the case, or if You are an IRA or other retail investor receiving this directly from us, we ask that
you inform us immediately.

In July 2018, Deutsche Bank revised its rating system for short term ideas whereby the branding has been changed to
Catalyst Calls (“CC”) from SOLAR ideas; the rating categories for Catalyst Calls originated in the Americas region have
been made consistent with the categories used by Analysts globally; and the effective time period for CCs has been
reduced from a maximum of 180 days to 90 days.

United States: Approved and/or distributed by Deutsche Bank Securities Incorporated, a member of FINRA, NFA and
SIPC. Analysts located outside of the United States are employed by non-US affiliates that are not subject to FINRA
regulations.

Germany: Approved and/or distributed by Deutsche Bank AG, a joint stock corporation with limited liability incorporated
in the Federal Republic of Germany with its principal office in Frankfurt am Main. Deutsche Bank AG is authorized under
German Banking Law and is subject to supervision by the European Central Bank and by BaFin, Germany's Federal
Financial Supervisory Authority.

United Kingdom: Approved and/or distributed by Deutsche Bank AG acting through its London Branch at Winchester
House, 1 Great Winchester Street, London EC2N 2DB. Deutsche Bank AG in the United Kingdom is authorised by the
Prudential Regulation Authority and is subject to limited regulation by the Prudential Regulation Authority and Financial
Conduct Authority. Details about the extent of our authorisation and regulation are available on request.

Hong Kong: Distributed by Deutsche Bank AG, Hong Kong Branch or Deutsche Securities Asia Limited (save that any
research relating to futures contracts within the meaning of the Hong Kong Securities and Futures Ordinance Cap. 571
shall be distributed solely by Deutsche Securities Asia Limited). The provisions set out above in the "Additional
Information" section shall apply to the fullest extent permissible by local laws and regulations, including without limitation
the Code of Conduct for Persons Licensed or Registered with the Securities and Futures Commission.

India: Prepared by Deutsche Equities India Private Limited (DEIPL) having CIN: U65990MH2002PTC137431 and
registered office at 14th Floor, The Capital, C-70, G Block, Bandra Kurla Complex Mumbai (India) 400051. Tel: + 91 22
7180 4444. It is registered by the Securities and Exchange Board of India (SEBI) as a Stock broker bearing registration
nos.: NSE (Capital Market Segment) - INB231196834, NSE (F&O Segment) INF231196834, NSE (Currency Derivatives
Segment) INE231196834, BSE (Capital Market Segment) INB011196830; Merchant Banker bearing SEBI Registration no.:
INM000010833 and Research Analyst bearing SEBI Registration no.: INH000001741. DEIPL may have received
administrative warnings from the SEBI for breaches of Indian regulations. The transmission of research through DEIPL is
Deutsche Bank's determination and will not make a recipient a client of DEIPL. Deutsche Bank and/or its affiliate(s) may
have debt holdings or positions in the subject company. With regard to information on associates, please refer to the
"Shareholdings" section in the Annual Report at: https://www.db.com/ir/en/annual-reports.htm.

Japan: Approved and/or distributed by Deutsche Securities Inc.(DSI). Registration number - Registered as a financial
instruments dealer by the Head of the Kanto Local Finance Bureau (Kinsho) No. 117. Member of associations: JSDA,
Type II Financial Instruments Firms Association and The Financial Futures Association of Japan. Commissions and risks
involved in stock transactions - for stock transactions, we charge stock commissions and consumption tax by multiplying
the transaction amount by the commission rate agreed with each customer. Stock transactions can lead to losses as a
result of share price fluctuations and other factors. Transactions in foreign stocks can lead to additional losses stemming
from foreign exchange fluctuations. We may also charge commissions and fees for certain categories of investment
advice, products and services. Recommended investment strategies, products and services carry the risk of losses to
principal and other losses as a result of changes in market and/or economic trends, and/or fluctuations in market value.
Before deciding on the purchase of financial products and/or services, customers should carefully read the relevant
disclosures, prospectuses and other documentation. "Moody's", "Standard & Poor's", and "Fitch" mentioned in this report
are not registered credit rating agencies in Japan unless Japan or "Nippon" is specifically designated in the name of the
entity. Reports on Japanese listed companies not written by analysts of DSI are written by Deutsche Bank Group's
analysts with the coverage companies specified by DSI. Some of the foreign securities stated on this report are not
disclosed according to the Financial Instruments and Exchange Law of Japan. Target prices set by Deutsche Bank's
equity analysts are based on a 12-month forecast period.

Page 42
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

Korea: Distributed by Deutsche Securities Korea Co.

South Africa: Deutsche Bank AG Johannesburg is incorporated in the Federal Republic of Germany (Branch Register
Number in South Africa: 1998/003298/10).

Singapore: This report is issued by Deutsche Bank AG, Singapore Branch or Deutsche Securities Asia Limited, Singapore
Branch (One Raffles Quay #18-00 South Tower Singapore 048583, +65 6423 8001), which may be contacted in respect
of any matters arising from, or in connection with, this report. Where this report is issued or promulgated by Deutsche
Bank in Singapore to a person who is not an accredited investor, expert investor or institutional investor (as defined in
the applicable Singapore laws and regulations), they accept legal responsibility to such person for its contents.

Taiwan: Information on securities/investments that trade in Taiwan is for your reference only. Readers should
independently evaluate investment risks and are solely responsible for their investment decisions. Deutsche Bank
research may not be distributed to the Taiwan public media or quoted or used by the Taiwan public media without written
consent. Information on securities/instruments that do not trade in Taiwan is for informational purposes only and is not
to be construed as a recommendation to trade in such securities/instruments. Deutsche Securities Asia Limited, Taipei
Branch may not execute transactions for clients in these securities/instruments.

Qatar: Deutsche Bank AG in the Qatar Financial Centre (registered no. 00032) is regulated by the Qatar Financial Centre
Regulatory Authority. Deutsche Bank AG - QFC Branch may undertake only the financial services activities that fall within
the scope of its existing QFCRA license. Its principal place of business in the QFC: Qatar Financial Centre, Tower, West
Bay, Level 5, PO Box 14928, Doha, Qatar. This information has been distributed by Deutsche Bank AG. Related financial
products or services are only available only to Business Customers, as defined by the Qatar Financial Centre Regulatory
Authority.

Russia: The information, interpretation and opinions submitted herein are not in the context of, and do not constitute,
any appraisal or evaluation activity requiring a license in the Russian Federation.

Kingdom of Saudi Arabia: Deutsche Securities Saudi Arabia LLC Company (registered no. 07073-37) is regulated by the
Capital Market Authority. Deutsche Securities Saudi Arabia may undertake only the financial services activities that fall
within the scope of its existing CMA license. Its principal place of business in Saudi Arabia: King Fahad Road, Al Olaya
District, P.O. Box 301809, Faisaliah Tower - 17th Floor, 11372 Riyadh, Saudi Arabia.

United Arab Emirates: Deutsche Bank AG in the Dubai International Financial Centre (registered no. 00045) is regulated
by the Dubai Financial Services Authority. Deutsche Bank AG - DIFC Branch may only undertake the financial services
activities that fall within the scope of its existing DFSA license. Principal place of business in the DIFC: Dubai International
Financial Centre, The Gate Village, Building 5, PO Box 504902, Dubai, U.A.E. This information has been distributed by
Deutsche Bank AG. Related financial products or services are available only to Professional Clients, as defined by the
Dubai Financial Services Authority.

Australia and New Zealand: This research is intended only for "wholesale clients" within the meaning of the Australian
Corporations Act and New Zealand Financial Advisors Act, respectively. Please refer to Australia-specific research
disclosures and related information at https://australia.db.com/australia/content/research-information.html Where
research refers to any particular financial product recipients of the research should consider any product disclosure
statement, prospectus or other applicable disclosure document before making any decision about whether to acquire the
product. In preparing this report, the primary analyst or an individual who assisted in the preparation of this report has
likely been in contact with the company that is the subject of this research for confirmation/clarification of data, facts,
statements, permission to use company-sourced material in the report, and/or site-visit attendance. Without prior
approval from Research Management, analysts may not accept from current or potential Banking clients the costs of
travel, accommodations, or other expenses incurred by analysts attending site visits, conferences, social events, and the
like. Similarly, without prior approval from Research Management and Anti-Bribery and Corruption ("ABC") team,
analysts may not accept perks or other items of value for their personal use from issuers they cover.

Page 43
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
15 January 2019
Quantcraft

# Additional information relative to securities, other financial products or issuers discussed in this report is available upon
# request. This report may not be reproduced, distributed or published without Deutsche Bank's prior written consent.
Copyright © 2019 Deutsche Bank AG

Page 44
Deutsche Bank AG/London

Provided for the exclusive use of hugues.demurard@exoduspoint.com on 2022-11-25T15:30+00:00. DO NOT REDISTRIBUTE
[Figure: Organizational Chart of Deutsche Bank Research including David Folkerts-Landau as Group Chief Economist and Global Head of Research, with various heads for APAC, EMEA, Americas Research, Debt, Thematic, Rates, FX, Germany, Quantitative and QIS Research. Below it is a list of International Production Locations.]