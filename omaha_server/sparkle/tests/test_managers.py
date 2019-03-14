# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from override_storage import override_storage

from sparkle.models import SparkleVersion
from sparkle.factories import SparkleVersionFactory


class VersionManagerTest(TestCase):
    @override_storage()
    def test_filter_by_enabled(self):
        version = SparkleVersionFactory.create(
            version='2062.125',
            file=SimpleUploadedFile('./chrome_installer.exe', False))
        version_disabled = SparkleVersionFactory.create(
            app=version.app,
            channel=version.channel,
            is_enabled=False,
            version='2062.126',
            file=SimpleUploadedFile('./chrome_installer2.exe', False))

        self.assertEqual(SparkleVersion.objects.all().count(), 2)
        self.assertEqual(SparkleVersion.objects.filter_by_enabled().count(), 1)
        self.assertIn(version, SparkleVersion.objects.filter_by_enabled())
        self.assertNotIn(version_disabled, SparkleVersion.objects.filter_by_enabled())

    def test_get_size(self):
        file_size = 42
        SparkleVersionFactory.create_batch(10, file_size=file_size)
        size = SparkleVersion.objects.get_size()
        self.assertEqual(size, file_size*10)
