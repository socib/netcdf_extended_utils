__author__ = 'ksebastian'


class FeatureTypeValue:

    time_series = 'timeSeries'
    time_series_profile = 'timeSeriesProfile'
    profile = 'profile'
    trajectory = 'trajectory'
    trajectory_profile = 'trajectoryProfile'

    @staticmethod
    def get_available_feature_type_values():
        """


        :return:
        """
        return FeatureTypeValue.time_series + ' ' + FeatureTypeValue.time_series_profile + ' ' + \
               FeatureTypeValue.trajectory + ' ' + FeatureTypeValue.trajectory_profile


class CFRoleValue:

    time_series_id = 'timeseries_id'
    profile_id = 'profile_id'
    trajectory_id = 'trajectory_id'


class AttributeName:

    # Global attributes
    feature_type = 'featureType'
    cf_feature_type = 'CF:featureType'
    cdm_data_type = 'cdm_data_type'

    # Variable attributes
    cf_role = 'cf_role'
    long_name = 'long_name'


class DimensionName:
    name_strlen = 'name_strlen'


class VariableName:
    station_name = 'station_name'
    profile = 'profile'
    trajectory = 'trajectory'

