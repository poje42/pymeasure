
import serial.tools.list_ports
import gc

from instrument_list import instrument_dict
from importlib import import_module
from pymeasure.instruments import Instrument


class InstrumentRegister:
    IdCache = None

    def import_class_from_string(path):
        module_path, _, class_name = path.rpartition('.')
        mod = import_module(module_path)
        klass = getattr(mod, class_name)
        return klass

    def create_dynamic_class(base_classes, class_name, class_attributes):
        # Create a dictionary for class attributes/methods
        class_dict = {}

        # Add attributes to the class dictionary
        class_dict.update(class_attributes)

        # Create the class dynamically using type()
        dynamic_class = type(class_name, base_classes, class_dict)

        return dynamic_class


    @classmethod
    def populateIdCache(self):
        self.IdCache = dict()
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in ports:
            # print(port,desc,hwid)
            if "067B:2303" in hwid:  # Keysight interface
                meter = self.import_class_from_string("pymeasure.instruments.agilent.AgilentU1252B")(port)
                id = meter.id
                if id != '':
                    self.IdCache[id[2]] = port

    @classmethod
    def clearIdCache(self):
        self.IdCache = None

    @classmethod
    def get_instrument_class(self, instr, **kwargs):
        if instr == 'None':
            return None
        else:
            kwargs = {**instrument_dict[instr].settings, **kwargs}
            adr = instrument_dict[instr].adr
            if adr == 'COM?':
                if not self.IdCache:
                    self.populateIdCache()

                if instrument_dict[instr].serialId in self.IdCache:
                    adr = self.IdCache[instrument_dict[instr].IdCache]
                else:
                    return None

            print(f"Instr {instr}")
            print("Driver: " + instrument_dict[instr].driver)
            print("Addr  : " + adr)

            ch = kwargs.pop('channel', None)
            if ch:
                for obj in gc.get_objects():
                    if isinstance(obj, Instrument):
                        if obj.adapter.resource_name == adr:
                            instr_class = obj
                            break
                else:
                    instr_class = self.import_class_from_string(instrument_dict[instr].driver)(adr, **kwargs)
                instr_class = getattr(instr_class, ch)
            else:
                instr_class = self.import_class_from_string(instrument_dict[instr].driver)(adr, **kwargs)
            return instr_class


def PrintDictionary(dictionary):
    for index, label in enumerate(dictionary):
        if not label == "None":
            descr = dictionary[label].driver.replace('pymeasure.instruments.', '').split('.')
            make = descr[0].capitalize()
            model = descr[1].capitalize()
            print("{}: {} \t {} \t {}".format(index, label, make, model))

# if __name__ == "__main__":
#     print("\n== RF Generators ==")
#     PrintDictionary( sl_instrument_list.RF_Gen_dict )

#     print("\n== Spectrum Analysers ==")
#     PrintDictionary( sl_instrument_list.RF_Spec_dict )

#     print("\n== Function Generators ==")
#     PrintDictionary( sl_instrument_list.Func_Gen_dict )

#     print("\n== Temperature Meters ==")
#     PrintDictionary( sl_instrument_list.Temp_Meter_dict )

#     print("\n== Power Supplies ==")
#     PrintDictionary( sl_instrument_list.PSU_dict )

#     print("\n== Digital MultiMeters (DMM) ==")
#     PrintDictionary( sl_instrument_list.DMM_dict )

#     print("\n== Counters ==")
#     PrintDictionary( sl_instrument_list.Counter_dict )

#     print("\n== Temperature Chambers ==")
#     PrintDictionary( sl_instrument_list.Temp_Chamber_dict )

#     print("\n== All Devices ==")
#     PrintDictionary( sl_instrument_list.instr_dict )
