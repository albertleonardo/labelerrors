# Pervasive Label Errors in Seismological Machine Learning Datasets
This is an effort to improve the datasets used for training deep learning models for observational seismology.
There are performance imporvements from culled datasets beyond what can be gained from addig model complexity with a fixed dataset.
See for example and inspiration:
[https://www.youtube.com/watch?v=06-AZXmwHjo] minute 5-10 

For analog studies in other fields and other datasets check this one out:
[https://labelerrors.com/]



We documented a series of erros or faulty labels in a number of machine learning datasets, focused on local earthquake recordings

There is a csv file for every dataset analyzed that contains the names and reeerence to the exmaples in the datasets per their Seisbench metadata. This is with the goal of avoiding them when training and testing.

## Examples

Some examples are shown here, mostly earthquakes that are not labeled might hurt model performance, as they are trained to recognize the labeled earthquakes while ignoring the unlabeled ones, which is precisely what we don't want them to do.

![Image Alt text](/images/aq2009_0000080.png)

## Noise samples 
We quantified the number of noise samples that do contain unlabeled earthquakes, here some examples from the four datasets that contain noise samples. 

![Image Alt text](/images/txed_172405.png)
![Image Alt text](/images/stead_0022054.png)
![Image Alt text](/images/pnw_000119.png)
![Image Alt text](/images/instance_0002650.png)


## Other errors
We found other forms of errors, for which their prevalence was not quantified (yet)
The data does not contain the labeled arrivals, due to archival or instrumental issues
![Image Alt text](/images/ceed_1001553.png)

The labels are inaccurate, for instance the S arrival label in this sample is too early
![Image Alt text](/images/instance_0548673.png)



Manuscript is coming
