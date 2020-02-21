from unittest import mock

from use_cases import create_shipment, API_URL

def test_create_shipment_does_post_to_external_api():
    with mock.patch('cargo_api.requests') as mock_requests:
        shipment = create_shipment({'sku1': 10}, incoterm='EXW')
        expected_data = {
            'client_reference': shipment.reference,
            'arrival_date': None,
            'products': [{'sku': 'sku1', 'quantity': 10}],
        }
        assert mock_requests.post.call_args == mock.call(
            API_URL + '/shipments/', json=expected_data
        )


def test_does_PUT_if_shipment_already_exists():
    with mock.patch('use_cases.uuid') as mock_uuid, mock.patch('cargo_api.requests') as mock_requests:
        mock_uuid.uuid4.return_value.hex = 'our-id'
        mock_requests.get.return_value.json.return_value = {
            'items': [{'id': 'their-id', 'client_reference': 'our-id'}]
        }

        shipment = create_shipment({'sku1': 10}, incoterm='EXW')
        assert mock_requests.post.called is False
        expected_data = {
            'client_reference': 'our-id',
            'arrival_date': None,
            'products': [{'sku': 'sku1', 'quantity': 10}],
        }
        assert mock_requests.put.call_args == mock.call(
            API_URL + '/shipments/their-id/', json=expected_data
        )


def test_does_PUT_if_shipment_already_exists2():
    with mock.patch('use_cases.cargo_api._get_shipment_id') as mock_get_shipment_id, mock.patch('cargo_api.requests') as mock_requests:
        mock_get_shipment_id.return_value = 'their-id'
        mock_requests.get.return_value.json.return_value = {
            'items': [{'id': 'their-id', 'client_reference': 'our-id'}]
        }

        shipment = create_shipment({'sku1': 10}, incoterm='EXW')
        assert mock_requests.post.called is False
        expected_data = {
            'client_reference': shipment.reference,
            'arrival_date': None,
            'products': [{'sku': 'sku1', 'quantity': 10}],
        }
        assert mock_requests.put.call_args == mock.call(
            API_URL + '/shipments/their-id/', json=expected_data
        )

