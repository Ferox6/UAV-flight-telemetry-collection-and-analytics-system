from orangebox import Parser


def parse_log_file(file_path: str):
    try:
        parser = Parser.load(file_path, allow_invalid_header=True)
        field_names = parser.field_names
        headers = parser.headers

        poles         = headers.get('motor_poles', 14)
        vbat_scale    = headers.get('vbat_scale', 110)
        vbatref       = headers.get('vbatref', 2442)
        current_scale = headers.get('currentSensor', [0, 386])[1] or 386

        field_idx = {name: i for i, name in enumerate(field_names)}

        def get_val(data_tuple, field, default=0):
            idx = field_idx.get(field)
            if idx is None or idx >= len(data_tuple):
                return default
            val = data_tuple[idx]
            if val == '' or val is None:
                return default
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        data = []
        try:
            for frame in parser.frames():
                if frame.type.name != 'INTRA':
                    continue

                raw = frame.data

                vbat_raw     = get_val(raw, 'vbatLatest')
                voltage      = round(vbat_raw * vbat_scale / (vbatref * 10), 3) if vbatref else 0

                rssi_raw     = get_val(raw, 'rssi')
                rssi_pct     = round(rssi_raw / 1023 * 100, 1) if rssi_raw > 0 else 0

                amp_raw      = get_val(raw, 'amperageLatest')
                amperage     = round(amp_raw / current_scale, 2) if current_scale else 0

                roll = get_val(raw, 'attitude[0]') or get_val(raw, 'roll')
                pitch = get_val(raw, 'attitude[1]') or get_val(raw, 'pitch')
                yaw = get_val(raw, 'attitude[2]') or get_val(raw, 'yaw')

                data.append({
                    "time":     round(get_val(raw, 'time') / 1e6, 4),
                    "ax":       get_val(raw, 'gyroADC[0]'),
                    "ay":       get_val(raw, 'gyroADC[1]'),
                    "az":       get_val(raw, 'gyroADC[2]'),
                    "voltage":  voltage,
                    "throttle": get_val(raw, 'rcCommand[3]'),
                    "rssi":     rssi_pct,
                    "amperage": amperage,
                    "m1":       get_val(raw, 'motor[0]'),
                    "m2":       get_val(raw, 'motor[1]'),
                    "m3":       get_val(raw, 'motor[2]'),
                    "m4":       get_val(raw, 'motor[3]'),
                    "rpm1":     round(get_val(raw, 'eRPM[0]') * 2 / poles, 0),
                    "rpm2":     round(get_val(raw, 'eRPM[1]') * 2 / poles, 0),
                    "rpm3":     round(get_val(raw, 'eRPM[2]') * 2 / poles, 0),
                    "rpm4":     round(get_val(raw, 'eRPM[3]') * 2 / poles, 0),
                    "roll_p":   get_val(raw, 'axisP[0]'),
                    "pitch_p":  get_val(raw, 'axisP[1]'),
                    "yaw_p":    get_val(raw, 'axisP[2]'),
                    "roll":     roll,
                    "pitch":    pitch,
                    "yaw":      yaw,
                })
        except RuntimeError:
            pass

        def get_header_value(*keys):
            if not headers:
                return ''
            lower_headers = {k.lower(): v for k, v in headers.items() if v not in (None, '')}
            for key in keys:
                if key in headers and headers[key] not in (None, ''):
                    return headers[key]
                value = lower_headers.get(key.lower())
                if value not in (None, ''):
                    return value
            return ''

        board_info = get_header_value(
            'Board information',
            'Board info',
            'Board name',
            'board_name',
            'board_info',
            'board',
            'Flight controller',
            'flight_controller',
        )
        firmware = get_header_value(
            'Firmware revision',
            'Firmware',
            'Firmware name',
            'firmware_name',
            'firmware_revision',
            'fw',
            'fw_version',
        )

        if data:
            print(f"[parser] точок: {len(data)}")
            print(f"[parser] перша точка: {data[0]}")
        else:
            print("[parser] данних не існує!")

        return data, {
            "board_info": board_info,
            "firmware": firmware,
        }

    except Exception as e:
        print(f"Критична помилка парсингу: {e}")
        return [], {}