
# Pervasive Label Errors in Seismological Machine Learning Datasets
This is an effort to improve the datasets used for training deep learning models for observational seismology.

We documented a series of erros or faulty labels in a number of machine learning datasets, focused on local earthquake recordings

There is a csv file for every dataset analyzed that contains the names and reeerence to the exmaples in the datasets per their Seisbench metadata. This is with the goal of avoiding them when training and testing.

## Examples

Some examples are shown here, mostly earthquakes that are not labeled might hurt model performance, as they are trained to recognize the labeled earthquakes while ignoring the unlabeled ones, which is precisely what we don't want them to do.

![Image Alt text](/images/aq2009_0000080.png)


Manuscript is coming
