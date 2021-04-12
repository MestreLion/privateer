initial = {
    "FORM-00": {
        "PLAYSCOR": b'\x00\x00\x00\x00\x00\x00\xce\xff'
                    b'\x00\x00\xce\xff\x80\xff\x7f\x00'
                    b'\x80\xff',
        "KILL": b'\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00',
    },
    "FORM-01": {
        "SSSSORIG": b'3;;==<<>',
        "SECT": b'3;;==<<>',
    },
    "FORM-02": {
        "REALFORM-03": {
            "FITECTRL": b'PLAYPLAN',
            "FORM-04": {
                "WEAPGUNS": b'\x05\x02\x00\x00',
                "LNCH": b'2\x04\x00\x00',
                "MISL": b'\x04\x05\x00',
                "tail": b'F'  # The (in)famous "FFORM"
            },
            "FORM-05": {
                "ENERINFO": b'ENERGY\x00\x00'
                            b'\x01\x02\x06\x01',
                "DAMG": b'\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00',
            },
            "FORM-06": {
                "MOBIDAMG": b'\x00\x00\x00\x00\x00\x00\x00\x00'
                            b'\x00\x00\x00\x00\x00\x00\x00\x00'
                            b'\x00\x00'
            },
            "FORM-07": {
                "SHLDINFO": b'SHIELDS\x00'
                            b'Z',
                "AARMR": b'\xfa\x00\xfa\x00\xfa\x00\xfa\x00'
                         b'\xfa\x00\xfa\x00\xfa\x00\xfa\x00',
                "DAMG": b'\x00\x00'
            },
            "FORM-08": {
                "TRGTINFO": b'TARGETNG'
                            b'=',
                "DDAMG": b'\x00\x00',
            },
            "FORM-09": {
                "CRGOINFO": b'CARGO\x00\x00\x00'
                            b'\x00',
                "CCRGI": b'\xd0\x07\x00\x00d\x00\x00\x00',
                "DATA": b'',
                "DAMG": b'\x00\x00',
            },
            "NAVQ": b'\x01',
            "tail": b'a'  # Overlapping first character of Player Name
        }
    }
}

midgame_example = {
    "FORM-00": {
        "PLAYSCOR": b'\x0f\x01\x94\xff\xbb\x00v\xff'
                    b'\xbb\x00\xce\xfe\x80\xff\x7f\x00\x14\xfd',
        "KILL": b'\x01\x00\x16\x00\x00\x00$\x00'
                b'\x02\x00\xa3\x00\x00\x00\x00\x00|\x00',
    },
    "FORM-01": {
        "SSSSORIG": b'3;;==<<>',
        "SECT": b'3;;==<<>'
    },
    "FORM-02": {
        "REALFORM-03": {
            "FITECTRL": b'PLAYPLAN',
            "FORM-04": {
                "WEAPGUNS": b'\x07\x02\x00\x00\x07\x03\x00\x00'
                            b'\x07\x01\x00\x00\x07\x04\x00\x00',
                "LNCH": b'2\x02\x00\x002\x03\x00\x004\x06\x00\x00',
                "MISL": b'\x03\x14\x00',
                "tail": b'F'
            },
            "FORM-05": {
                "ENERINFO": b'ENERGY\x00\x00'
                            b'\x01\x02\x03\x01\x04\x01\x05\x01\x06\x02',
                "DAMG": b'\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00',
            },
            "FORM-06": {
                "MOBIDAMG": b'\x00\x00\x00\x00\x00\x00\x00\x00'
                            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            },
            "FORM-07": {
                "SHLDINFO": b'SHIELDS\x00[',
                "AARMR": b'\xf4\x01\xf4\x01\xf4\x01\xf4\x01'
                         b'\xf4\x01\xf4\x01\xf4\x01\xf4\x01',
                "DAMG": b'\x00\x00',
            },
            "FORM-08": {
                "TRGTINFO": b'TARGETNG'
                            b'D',
                "DDAMG": b'\x00\x00',
            },
            "FORM-09": {
                "CRGOINFO": b'CARGO\x00\x00\x00\x00',
                "CCRGI": b'P\xaf\t\x002\x00\x01\x00',  # Hard-earned with my sweat!
                "DATA": b'*\x01\x00\x01\x0e\x05\x00\x00',
                "DAMG": b'\x00\x00',
            },
            "FORM-10": {
                "JDRVINFO": b'\x06\x00\x06\x00',
                "FORM-11": {
                    "DAMGDAMG": b'\x90\x01\x03\x00',
                },
                "DAMG": b'\x00\x00',
            },
            "TRRT": b'\x01',
            "RREPR": b'\x90\x01\x00\x00',
            "AFTB": b'',
            "ECMS": b'K',
            "NNAVQ": b'\x0f',
            "tail": b'R'
        }
    }
}
