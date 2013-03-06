#!/usr/bin/env python

"""
Script that generates C code for compact storage of settings.

In C settigns are represented as a top-level struct (which can then refer to
other structs). The first field of top-level struct must be a u32 version
field. A version support up to 4 components, each component in range <0,255>.
For example version "2.1.3" is encoded as: u32 version = (2 << 16) | (1 << 8) | 3

We support generating multiple top-level such structs.

In order to support forward and backward compatibility, struct for a given
version must be a strict superset of struct for a previous version. We can
only add, we can't remove fields or change their types (we can change the names
of fields).

By convention, settings for each version of Sumatra are in gen_settings_$ver.py
file. For example, settings for version 2.3 are in gen_settings_2_3.py.

That way we can inherit settings for version N from settings for version N-1.

We rely on an exact layout of data in the struct, so:
 - we don't use C types whose size is not fixed (e.g. int)
 - we use a fixed struct packing
 - our pointers are always 8 bytes, to support both 64-bit and 32-bit archs
   with the same definition

TODO:
 - add a notion of Struct inheritance to make it easy to support forward/backward
   compatibility
 - generate default data as serialized block
 - generate asserts that our assumptions about offsets of fields in the structs
   are correct
"""

import gen_settings_2_3

c_hdr = """
// DON'T EDIT MANUALLY !!!!
// auto-generated by scripts/gen_settings.py !!!!

template <typename T>
union Ptr {
    T *	      ptr;
    char      b[8];
}

STATIC_ASSERT(8 == sizeof(Ptr<int>), ptr_is_8_bytes);

"""

# works recursively. res is used to return a result, which is an array of
# strings corresponding to
def gen_c_for_struct(struct, res = None, top_level=True):
	if top_level:
		first = struct.fields[0]
		#print("name: %s, type: %s" % (first_field.name, first_field.typ))
		assert "version" == first.name and "u32" == first.typ

	lines = ["struct %s {" % struct.name]
	for field in struct.fields:
		s = "    %-24s %s;" % (field.c_type(), field.name)
		lines.append(s)
		if field.is_struct():
			gen_c_for_struct(field.typ, res, top_level=False)
	lines.append("};\n")
	res.append("\n".join(lines))

def gen_c():
	all_structs = []
	gen_c_for_struct(gen_settings_2_3.advancedSettings, all_structs)
	return "\n".join(all_structs)

def main():
	s = gen_c()
	print(c_hdr + s)

if __name__ == "__main__":
	main()