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


class Error(object):
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
        'status': 'int',
        'msg': 'str',
        'extras': 'str'
    }

    attribute_map = {
        'status': 'status',
        'msg': 'msg',
        'extras': 'extras'
    }

    def __init__(self, status=None, msg=None, extras=None):  # noqa: E501
        """Error - a model defined in Swagger"""  # noqa: E501
        self._status = None
        self._msg = None
        self._extras = None
        self.discriminator = None
        self.status = status
        self.msg = msg
        if extras is not None:
            self.extras = extras

    @property
    def status(self):
        """Gets the status of this Error.  # noqa: E501

        The returned HTTP status code  # noqa: E501

        :return: The status of this Error.  # noqa: E501
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Error.

        The returned HTTP status code  # noqa: E501

        :param status: The status of this Error.  # noqa: E501
        :type: int
        """
        if status is None:
            raise ValueError("Invalid value for `status`, must not be `None`")  # noqa: E501

        self._status = status

    @property
    def msg(self):
        """Gets the msg of this Error.  # noqa: E501

        A general message about the error.  # noqa: E501

        :return: The msg of this Error.  # noqa: E501
        :rtype: str
        """
        return self._msg

    @msg.setter
    def msg(self, msg):
        """Sets the msg of this Error.

        A general message about the error.  # noqa: E501

        :param msg: The msg of this Error.  # noqa: E501
        :type: str
        """
        if msg is None:
            raise ValueError("Invalid value for `msg`, must not be `None`")  # noqa: E501

        self._msg = msg

    @property
    def extras(self):
        """Gets the extras of this Error.  # noqa: E501

        A more detailed breakdown of the error  # noqa: E501

        :return: The extras of this Error.  # noqa: E501
        :rtype: str
        """
        return self._extras

    @extras.setter
    def extras(self, extras):
        """Sets the extras of this Error.

        A more detailed breakdown of the error  # noqa: E501

        :param extras: The extras of this Error.  # noqa: E501
        :type: str
        """

        self._extras = extras

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
        if issubclass(Error, dict):
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
        if not isinstance(other, Error):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
