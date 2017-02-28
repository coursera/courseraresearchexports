#!/usr/bin/env python

# Copyright 2016 Coursera
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from courseraresearchexports.models import utils
from mock import Mock
from mock import patch
import requests

fake_partner_short_name = 'fake_partner_short_name'
fake_partner_id = 1
fake_partner_response = {'elements': [ {"id": str(fake_partner_id)} ] }

@patch.object(requests, 'get')
def test_partner_id_lookup(mockget):
    mock_partners_get_response = Mock()
    mock_partners_get_response.json.return_value = fake_partner_response
    mockget.return_value = mock_partners_get_response
    inferred_partner_id = utils.lookup_partner_id_by_short_name(fake_partner_short_name)

    assert inferred_partner_id == fake_partner_id
