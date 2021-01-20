# Substantial Undocumented Infection Facilitates the Rapid Dissemination of Novel Coronavirus (SARS-CoV2)
## An application in context of Nepal  
  
We have implemented a SEIR model to simulate the spread of the Novel Coronavirus in districts of Nepal. This is a reproduction of 16 March 2020 paper by Li et al. The data required to feed into this model were extracted from various sources. Daily nummbers of infected individuals were extracted from Situation Reports published by National Disaster Risk Reduction and Management Activity (NDRRMA). The situation reports contain usable data from 29th March to 12th May. Ncell provided us with mobility data for 17 days, between 31 May and 16 June. The period for which we had the mobility data did not overlap with the period of infection data. Some extrapolation was required to approximate mobility during earlier dates. We took an assumption that since both periods were during nation wide lockdown, the mobility must have been similar as well. The latest official population data available is from the census of 2011. We used an estimated population generated from a machine learning model which was available in our Google Drive. All our data needed to be in district level granularity as we are modeling the spread of disease from district-to-district.

### Data requirement and cleaning

We required following data to reproduce the model as proposed by Li et al.

**1. Number of documented infections everyday in every district**
<p>This data was extracted from situation reports published by the NDRRMA. The reports were in pdf format and required some manual data extraction as well. We used an open-source tool called Tabula to semi-automate most of the data extraction process. After extraction, the data still had to be cleaned and verified. Although there are situation reports for more recent dates, they contain infection counts with provincial level aggregation, hence, these more recent situation reports could not be used. We decided to model the spread of disease using data between 29th March and 12th May. Finally, we had the data we needed in the following format:</p>
<table><tr>
    <th></th><th>2020-03-29</th><th>2020-03-30</th><th> . . .  </th><th>2020-05-11</th><th>2020-05-12</th>
    </tr><tr>
    <td>Achham</td><td>0.0</td><td>0.0</td><td> . . . </td><td>12.0</td><td>18.0</td></tr><tr>
    <td>Arghakhanchi</td><td>0.0</td><td>0.0</td><td> . . . </td><td>22.0</td><td>17.0</td></tr>
    <tr><th colspan=6 align=center> . </th></tr><tr><th colspan=6 align=center> . </th></tr><tr><th colspan=6 align=center> . </th></tr>
    <td>Udayapur</td><td>0.0</td><td>0.0</td><td> . . . </td><td>113.0</td><td>118.0</td></tr><tr>
</table>

**2. Number of people moving from one district to another district**
<p>
The mobility data provided by Ncell was in a format that could not be used with this model. They had provided us with data from 31st of May and 16th of June in the following format:
<table>
    <tr>
        <th>dayid1</th>
        <th>district1</th>
        <th>outgoing_cnt</th>
        <th>incoming_cnt</th>
    </tr>
    <tr>
        <td>20200531</td>
        <td>Achham</td>
        <td>812.0</td>
        <td>814.0</td>
    </tr>
    <tr>
        <td>20200601</td>
        <td>Achham</td>
        <td>819.0</td>
        <td>818.0</td>
    </tr>
    <tr><th colspan=6 align=center> . </th></tr><tr><th colspan=6 align=center> . </th></tr><tr><th colspan=6 align=center> . </th></tr>
    <tr>
        <td>20200531</td>
        <td>Arghakhanchi</td>
        <td>612.0</td>
        <td>610.0</td>
    </tr>
    <tr>
        <td>20200601</td>
        <td>Arghakhanchi</td>
        <td>652.0</td>
        <td>630.0</td>
    </tr>
</table>   

While, we needed something like this:
<table>
    <tr>
        <th></th>
        <th>Achham</th>
        <th>Arghakhanchi</th>
        <th> . . . </th>
        <th>Udayapur</th>
    </tr>
    <tr>
        <th>Achham</th>
        <td>0.0</td>
        <td>812.0</td>
        <td> . . . </td>
        <td>13.0</td>
    </tr>
    <tr>
        <th>Arghakhanchi</th>
        <td>816.0</td>
        <td>0.0</td>
        <td> . . . </td>
        <td>23.0</td>
    </tr>
        <tr><th colspan=6 align=center> . </th></tr><tr><th colspan=6 align=center> . </th></tr><tr><th colspan=6 align=center> . </th></tr>
    <tr>
        <th>Udayapur</th>
        <td>26.0</td>
        <td>33.0</td>
        <td> . . . </td>
        <td>0.0</td>
    </tr>
</table>

for each day between 31st March to 12th May.  

The dataset also contained some spelling errors which was rather straightforward to resolve. We used district spellings from other datasets we had as reference and made appropriate edits. The dataset had missing data for three districts, namely *Dolpa*, *Humla* and *Mustang*. We looked up what districts had the least number of people entering and leaving and discovered that those districts neighbored with the three missing districts. We concluded that there is no data for those districts because people simply did not move. The Ncell mobility dataset had data for *Kathmandu*, *Lalitpur* and *Bhaktapur* districts aggregated into one single *Kathmandu valley*. Similar aggregations could be seen for districts *Rasuwa East*, *Rasuwa West* and *Nawalparasi East*, *Nawalparasi West*. Given the fact that people move between districts of Kathmandu valley in significant numbers, we decided not to segregate the districts of valley. Corresponding changes were made to the other two datasets we had.  

We extrapolated the available data to earlier dates and then approximated the movement between each district using the incoming and outgoing counts. A brief summary of these two tasks are given below:
</p>

- **Extrapolate available data to earlier dates**
<p>
    We assumed, the mobility between dates 31st of March and 12th of May were similar to the mobility between dates 31st of May and 16th of June as they were both during the nation-wide lockdown. We extrapolated the mobility data by first creating a probability distribution of movement and resampled new approximated movement from that distribution. The new approximations were rather jumpy, with differences in mobility of consecutive days in thousands. We made these differences smoother by resampling 1000 times and taking an aggregate. The new approximations looked realistic with respect to their original counterparts, however, they were tightly centered around mean.
</p>

- **Approximate district-to-district movement**
<p>
    We used the following equation to approximate district-to-district movement for each district:
    
$$
Outgoing (_{origin \to destination}) = Incoming (_{destination}) * \frac{Outgoing (_{origin})}{Outgoing (_{total})}
$$
    
*This equation will most likely be revised in the future.*  
    
The resulting movement data **did not look unrealistic**. We decided to go ahead with this until we have better data, or idea.

</p>


**3. Population of each district**
<p>
    We had an approximation of current population available in our Google Drive. The approximation was generated using a machine learning model that used satellite imageries as one of its inputs.
</p>