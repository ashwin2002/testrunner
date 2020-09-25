# coding: utf-8

"""
    Couchbase Backup Service API

    This is REST API allows users to remotely schedule and run backups, restores and merges as well as to explore various archives for all there Couchbase Clusters.  # noqa: E501

    OpenAPI spec version: 0.1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class Repository(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'id': 'str',
        'plan_name': 'str',
        'state': 'str',
        'archive': 'str',
        'repo': 'str',
        'bucket': 'RepositoryBucket',
        'version': 'int',
        'health': 'RepositoryHealth',
        'scheduled': 'dict(str, RepositoryScheduled)',
        'running_tasks': 'dict(str, TaskRun)',
        'running_one_off': 'dict(str, TaskRun)',
        'creation_time': 'str',
        'update_time': 'str',
        'cloud_info': 'RepositoryCloudInfo'
    }

    attribute_map = {
        'id': 'id',
        'plan_name': 'plan_name',
        'state': 'state',
        'archive': 'archive',
        'repo': 'repo',
        'bucket': 'bucket',
        'version': 'version',
        'health': 'health',
        'scheduled': 'scheduled',
        'running_tasks': 'running_tasks',
        'running_one_off': 'running_one_off',
        'creation_time': 'creation_time',
        'update_time': 'update_time',
        'cloud_info': 'cloud_info'
    }

    def __init__(self, id=None, plan_name=None, state=None, archive=None, repo=None, bucket=None, version=None, health=None, scheduled=None, running_tasks=None, running_one_off=None, creation_time=None, update_time=None, cloud_info=None):  # noqa: E501
        """Repository - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._plan_name = None
        self._state = None
        self._archive = None
        self._repo = None
        self._bucket = None
        self._version = None
        self._health = None
        self._scheduled = None
        self._running_tasks = None
        self._running_one_off = None
        self._creation_time = None
        self._update_time = None
        self._cloud_info = None
        self.discriminator = None
        if id is not None:
            self.id = id
        if plan_name is not None:
            self.plan_name = plan_name
        if state is not None:
            self.state = state
        if archive is not None:
            self.archive = archive
        if repo is not None:
            self.repo = repo
        if bucket is not None:
            self.bucket = bucket
        if version is not None:
            self.version = version
        if health is not None:
            self.health = health
        if scheduled is not None:
            self.scheduled = scheduled
        if running_tasks is not None:
            self.running_tasks = running_tasks
        if running_one_off is not None:
            self.running_one_off = running_one_off
        if creation_time is not None:
            self.creation_time = creation_time
        if update_time is not None:
            self.update_time = update_time
        if cloud_info is not None:
            self.cloud_info = cloud_info

    @property
    def id(self):
        """Gets the id of this Repository.  # noqa: E501

        The unique ID for the repository  # noqa: E501

        :return: The id of this Repository.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Repository.

        The unique ID for the repository  # noqa: E501

        :param id: The id of this Repository.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def plan_name(self):
        """Gets the plan_name of this Repository.  # noqa: E501

        The base plan for this repository  # noqa: E501

        :return: The plan_name of this Repository.  # noqa: E501
        :rtype: str
        """
        return self._plan_name

    @plan_name.setter
    def plan_name(self, plan_name):
        """Sets the plan_name of this Repository.

        The base plan for this repository  # noqa: E501

        :param plan_name: The plan_name of this Repository.  # noqa: E501
        :type: str
        """

        self._plan_name = plan_name

    @property
    def state(self):
        """Gets the state of this Repository.  # noqa: E501


        :return: The state of this Repository.  # noqa: E501
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this Repository.


        :param state: The state of this Repository.  # noqa: E501
        :type: str
        """
        allowed_values = ["active", "paused", "archived", "imported"]  # noqa: E501
        if state not in allowed_values:
            raise ValueError(
                "Invalid value for `state` ({0}), must be one of {1}"  # noqa: E501
                .format(state, allowed_values)
            )

        self._state = state

    @property
    def archive(self):
        """Gets the archive of this Repository.  # noqa: E501

        The location for the backup archive  # noqa: E501

        :return: The archive of this Repository.  # noqa: E501
        :rtype: str
        """
        return self._archive

    @archive.setter
    def archive(self, archive):
        """Sets the archive of this Repository.

        The location for the backup archive  # noqa: E501

        :param archive: The archive of this Repository.  # noqa: E501
        :type: str
        """

        self._archive = archive

    @property
    def repo(self):
        """Gets the repo of this Repository.  # noqa: E501

        The backup repository for this repository  # noqa: E501

        :return: The repo of this Repository.  # noqa: E501
        :rtype: str
        """
        return self._repo

    @repo.setter
    def repo(self, repo):
        """Sets the repo of this Repository.

        The backup repository for this repository  # noqa: E501

        :param repo: The repo of this Repository.  # noqa: E501
        :type: str
        """

        self._repo = repo

    @property
    def bucket(self):
        """Gets the bucket of this Repository.  # noqa: E501


        :return: The bucket of this Repository.  # noqa: E501
        :rtype: RepositoryBucket
        """
        return self._bucket

    @bucket.setter
    def bucket(self, bucket):
        """Sets the bucket of this Repository.


        :param bucket: The bucket of this Repository.  # noqa: E501
        :type: RepositoryBucket
        """

        self._bucket = bucket

    @property
    def version(self):
        """Gets the version of this Repository.  # noqa: E501


        :return: The version of this Repository.  # noqa: E501
        :rtype: int
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this Repository.


        :param version: The version of this Repository.  # noqa: E501
        :type: int
        """

        self._version = version

    @property
    def health(self):
        """Gets the health of this Repository.  # noqa: E501


        :return: The health of this Repository.  # noqa: E501
        :rtype: RepositoryHealth
        """
        return self._health

    @health.setter
    def health(self, health):
        """Sets the health of this Repository.


        :param health: The health of this Repository.  # noqa: E501
        :type: RepositoryHealth
        """

        self._health = health

    @property
    def scheduled(self):
        """Gets the scheduled of this Repository.  # noqa: E501

        A map task name to next scheduled run  # noqa: E501

        :return: The scheduled of this Repository.  # noqa: E501
        :rtype: dict(str, RepositoryScheduled)
        """
        return self._scheduled

    @scheduled.setter
    def scheduled(self, scheduled):
        """Sets the scheduled of this Repository.

        A map task name to next scheduled run  # noqa: E501

        :param scheduled: The scheduled of this Repository.  # noqa: E501
        :type: dict(str, RepositoryScheduled)
        """

        self._scheduled = scheduled

    @property
    def running_tasks(self):
        """Gets the running_tasks of this Repository.  # noqa: E501

        A map task name to scheduled running task details  # noqa: E501

        :return: The running_tasks of this Repository.  # noqa: E501
        :rtype: dict(str, TaskRun)
        """
        return self._running_tasks

    @running_tasks.setter
    def running_tasks(self, running_tasks):
        """Sets the running_tasks of this Repository.

        A map task name to scheduled running task details  # noqa: E501

        :param running_tasks: The running_tasks of this Repository.  # noqa: E501
        :type: dict(str, TaskRun)
        """

        self._running_tasks = running_tasks

    @property
    def running_one_off(self):
        """Gets the running_one_off of this Repository.  # noqa: E501

        A map task name to one-off running task  # noqa: E501

        :return: The running_one_off of this Repository.  # noqa: E501
        :rtype: dict(str, TaskRun)
        """
        return self._running_one_off

    @running_one_off.setter
    def running_one_off(self, running_one_off):
        """Sets the running_one_off of this Repository.

        A map task name to one-off running task  # noqa: E501

        :param running_one_off: The running_one_off of this Repository.  # noqa: E501
        :type: dict(str, TaskRun)
        """

        self._running_one_off = running_one_off

    @property
    def creation_time(self):
        """Gets the creation_time of this Repository.  # noqa: E501

        The time the repository was created. Time is in RFC3339 format.  # noqa: E501

        :return: The creation_time of this Repository.  # noqa: E501
        :rtype: str
        """
        return self._creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        """Sets the creation_time of this Repository.

        The time the repository was created. Time is in RFC3339 format.  # noqa: E501

        :param creation_time: The creation_time of this Repository.  # noqa: E501
        :type: str
        """

        self._creation_time = creation_time

    @property
    def update_time(self):
        """Gets the update_time of this Repository.  # noqa: E501

        The last time the repository was updated. Time is in RFC3339  # noqa: E501

        :return: The update_time of this Repository.  # noqa: E501
        :rtype: str
        """
        return self._update_time

    @update_time.setter
    def update_time(self, update_time):
        """Sets the update_time of this Repository.

        The last time the repository was updated. Time is in RFC3339  # noqa: E501

        :param update_time: The update_time of this Repository.  # noqa: E501
        :type: str
        """

        self._update_time = update_time

    @property
    def cloud_info(self):
        """Gets the cloud_info of this Repository.  # noqa: E501


        :return: The cloud_info of this Repository.  # noqa: E501
        :rtype: RepositoryCloudInfo
        """
        return self._cloud_info

    @cloud_info.setter
    def cloud_info(self, cloud_info):
        """Sets the cloud_info of this Repository.


        :param cloud_info: The cloud_info of this Repository.  # noqa: E501
        :type: RepositoryCloudInfo
        """

        self._cloud_info = cloud_info

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(Repository, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Repository):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
