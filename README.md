# cold-climate-data-comparison

This repository contains scripts and data files intended to explore the performance of wind lidar and meteorological towers in cold climates. The codes have been provided by [Nergica](https://nergica.com/) as part of a joint [IEA Wind Task 32](https://iea-wind.org/task32/) / [IEA Wind Task 19](https://iea-wind.org/task19/) working group on the use of wind lidar in cold climates.

The repository includes:

- _ScriptTask32\_CorrelationLidarMetMast\_Nergica.py_ to compare measurements from a wind lidar with data from a meteorological mast. The comparisons can be shown as functions of other metrics. For more details refer to the code.
- _ScriptTask32\_LidarDataAvailability\_MetMast\_Nergica.py_ to analyze lidar data availability as a function of environmental parameters. For more details refer to the code.
- _QualityControl_Nergica.pdf_ describes the quality control routines used to check that data are appropriate.
- _./metmastData/mmv*.csv_ are data files of exemplary meteorological data to be used in the comparison.
- _./lidarData/*dataWindCube.pkl_  are data files of exemplary wind lidar data to be used in the comparison.

The codes and their results are intended to be the basis for discussion. All constructive comments are welcome!

## License
The python scripts (_*.py_) in this repository were created by Nergica and are made available under the MIT license.

The data files (_*.csv_, _*.pkl_) in the _./lidarData/_ and _./metMastData/_ directories in this repository were supplied by Nergica for demonstration purposes only and remain the property of Nergica. They may not be used for any other purpose.

## Update history
- 2021 October 15: repository cleaned up, first release candidate committed (V 0.1)
- 2021 October 12: first upload

# How to provide feedback to this repository
We welcome constructive feedback on these codes. There are several ways to do this:

## ... through Github
You can provide feedback by [raising an issue](https://github.com/IEA-Wind-Task-32/cold-climate-data-comparison/issues). Before you raise an issue, please take a few minutes to check if there is a similar one in the list already.

**You will have to be logged in to Github to provide feedback**. This means that your feedback will be associated with your username, which may make it possible to identify you. We prefer to have feedback associated with a name because this is a community effort.

## ... via the IEA Wind Task 32 Operating Agent
Please send your feedback to [ieawind.task32@ifb.uni-stuttgart.de](mailto:ieawind.task32@ifb.uni-stuttgart.de). Please note that your email may be forwarded.

# Contributors
Please see https://github.com/IEA-Wind-Task-32/cold-climate-data-comparison/community_contributors for a complete list of contributors.

The code was originally supplied by Marc Defossez, Nergica

The repository was created by, and is maintained by Andy Clifton [![ORCID](https://orcid.org/sites/default/files/images/orcid_16x16.png)](https://orcid.org/0000-0001-9698-5083)