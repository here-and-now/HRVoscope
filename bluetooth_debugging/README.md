# H10 Services

Name: Polar H10
	All Services

		Description: Device Information
		Service: 0000180a-0000-1000-8000-00805f9b34fb (Handle: 20): Device Information

		Description: Unknown
		Service: 6217ff4b-fb31-1140-ad5a-a45545d7ecf3 (Handle: 39): Unknown

		Description: Battery Service
		Service: 0000180f-0000-1000-8000-00805f9b34fb (Handle: 35): Battery Service

		Description: Heart Rate
		Service: 0000180d-0000-1000-8000-00805f9b34fb (Handle: 14): Heart Rate

		Description: Unknown
		Service: fb005c80-02e7-f387-1cad-8acd2d8df0c8 (Handle: 45): Unknown

		Description: Polar Electro Oy
		Service: 0000feee-0000-1000-8000-00805f9b34fb (Handle: 52): Polar Electro Oy

		Description: Generic Attribute Profile
		Service: 00001801-0000-1000-8000-00805f9b34fb (Handle: 10): Generic Attribute Profile

	Service Characteristics:

		Description: Device Information
		Service: 0000180a-0000-1000-8000-00805f9b34fb (Handle: 20): Device Information
		Characteristics:

			UUID: 00002a25-0000-1000-8000-00805f9b34fb
			Descipriton: Serial Number String
			Handle: 25
			Properties: ['read']
			Descriptors:

			UUID: 00002a27-0000-1000-8000-00805f9b34fb
			Descipriton: Hardware Revision String
			Handle: 27
			Properties: ['read']
			Descriptors:

			UUID: 00002a26-0000-1000-8000-00805f9b34fb
			Descipriton: Firmware Revision String
			Handle: 29
			Properties: ['read']
			Descriptors:

			UUID: 00002a23-0000-1000-8000-00805f9b34fb
			Descipriton: System ID
			Handle: 33
			Properties: ['read']
			Descriptors:

			UUID: 00002a28-0000-1000-8000-00805f9b34fb
			Descipriton: Software Revision String
			Handle: 31
			Properties: ['read']
			Descriptors:

			UUID: 00002a24-0000-1000-8000-00805f9b34fb
			Descipriton: Model Number String
			Handle: 23
			Properties: ['read']
			Descriptors:

			UUID: 00002a29-0000-1000-8000-00805f9b34fb
			Descipriton: Manufacturer Name String
			Handle: 21
			Properties: ['read']
			Descriptors:

		Description: Unknown
		Service: 6217ff4b-fb31-1140-ad5a-a45545d7ecf3 (Handle: 39): Unknown
		Characteristics:

			UUID: 6217ff4c-c8ec-b1fb-1380-3ad986708e2d
			Descipriton: Unknown
			Handle: 40
			Properties: ['read']
			Descriptors:

			UUID: 6217ff4d-91bb-91d0-7e2a-7cd3bda8a1f3
			Descipriton: Unknown
			Handle: 42
			Properties: ['write-without-response', 'indicate']
			Descriptors:
				00002902-0000-1000-8000-00805f9b34fb (Handle: 44): Client Characteristic Configuration

		Description: Battery Service
		Service: 0000180f-0000-1000-8000-00805f9b34fb (Handle: 35): Battery Service
		Characteristics:

			UUID: 00002a19-0000-1000-8000-00805f9b34fb
			Descipriton: Battery Level
			Handle: 36
			Properties: ['read', 'notify']
			Descriptors:
				00002902-0000-1000-8000-00805f9b34fb (Handle: 38): Client Characteristic Configuration

		Description: Heart Rate
		Service: 0000180d-0000-1000-8000-00805f9b34fb (Handle: 14): Heart Rate
		Characteristics:

			UUID: 00002a37-0000-1000-8000-00805f9b34fb
			Descipriton: Heart Rate Measurement
			Handle: 15
			Properties: ['notify']
			Descriptors:
				00002902-0000-1000-8000-00805f9b34fb (Handle: 17): Client Characteristic Configuration

			UUID: 00002a38-0000-1000-8000-00805f9b34fb
			Descipriton: Body Sensor Location
			Handle: 18
			Properties: ['read']
			Descriptors:

		Description: Unknown
		Service: fb005c80-02e7-f387-1cad-8acd2d8df0c8 (Handle: 45): Unknown
		Characteristics:

			UUID: fb005c81-02e7-f387-1cad-8acd2d8df0c8
			Descipriton: Unknown
			Handle: 46
			Properties: ['read', 'write', 'indicate']
			Descriptors:
				00002902-0000-1000-8000-00805f9b34fb (Handle: 48): Client Characteristic Configuration

			UUID: fb005c82-02e7-f387-1cad-8acd2d8df0c8
			Descipriton: Unknown
			Handle: 49
			Properties: ['notify']
			Descriptors:
				00002902-0000-1000-8000-00805f9b34fb (Handle: 51): Client Characteristic Configuration

		Description: Polar Electro Oy
		Service: 0000feee-0000-1000-8000-00805f9b34fb (Handle: 52): Polar Electro Oy
		Characteristics:

			UUID: fb005c53-02e7-f387-1cad-8acd2d8df0c8
			Descipriton: Unknown
			Handle: 59
			Properties: ['write-without-response', 'write']
			Descriptors:

			UUID: fb005c51-02e7-f387-1cad-8acd2d8df0c8
			Descipriton: Unknown
			Handle: 53
			Properties: ['write-without-response', 'write', 'notify']
			Descriptors:
				00002902-0000-1000-8000-00805f9b34fb (Handle: 55): Client Characteristic Configuration

			UUID: fb005c52-02e7-f387-1cad-8acd2d8df0c8
			Descipriton: Unknown
			Handle: 56
			Properties: ['notify']
			Descriptors:
				00002902-0000-1000-8000-00805f9b34fb (Handle: 58): Client Characteristic Configuration

		Description: Generic Attribute Profile
		Service: 00001801-0000-1000-8000-00805f9b34fb (Handle: 10): Generic Attribute Profile
		Characteristics:

			UUID: 00002a05-0000-1000-8000-00805f9b34fb
			Descipriton: Service Changed
			Handle: 11
			Properties: ['indicate']
			Descriptors:
				00002902-0000-1000-8000-00805f9b34fb (Handle: 13): Client Characteristic Configuration
