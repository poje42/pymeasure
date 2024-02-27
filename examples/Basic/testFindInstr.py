from instrument_register import InstrumentRegister


# from pymeasure.instruments.resources import list_resources

# print(list_resources())
voltMeterId = 'ID017'
voltMeterObj = InstrumentRegister.get_instrument_class(voltMeterId)


# print(instrument_dict[voltMeterId])
dir(voltMeterObj)


psuId = 'ID030:1'
psuObj = InstrumentRegister.get_instrument_class(psuId)

psu2Id = 'ID030:2'
psu2Obj = InstrumentRegister.get_instrument_class(psu2Id)

print(voltMeterObj)
print(psuObj)
print(psu2Obj)
psuObj.voltage_setpoint = 1
psu2Obj.voltage_setpoint = 2

# import gc
# for obj in gc.get_objects():
    # print(obj)
    # if isinstance(obj, some_class):
    #     dome_something(obj)

# print(globals())