#!/usr/bin/env python3
"""Add STAT table to static fonts."""

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
import sys


def add_stat_table(font_path):
    """Add STAT table to a static font."""
    font = TTFont(font_path)
    filename = font_path.split("/")[-1]

    # Determine font style from filename
    is_italic = "Italic" in filename
    is_bold = "Bold" in filename

    # Create STAT table
    stat = otTables.STAT()
    stat.Version = 0x00010001

    # Create design axes
    wght_axis = otTables.AxisRecord()
    wght_axis.AxisTag = "wght"
    wght_axis.AxisNameID = _add_name(font, "Weight")
    wght_axis.AxisOrdering = 0

    ital_axis = otTables.AxisRecord()
    ital_axis.AxisTag = "ital"
    ital_axis.AxisNameID = _add_name(font, "Italic")
    ital_axis.AxisOrdering = 1

    stat.DesignAxisRecord = otTables.AxisRecordArray()
    stat.DesignAxisRecord.Axis = [wght_axis, ital_axis]

    # Create axis values
    axis_values = []

    if is_italic:
        # Weight: Regular
        wght_val = otTables.AxisValue()
        wght_val.Format = 1
        wght_val.AxisIndex = 0
        wght_val.Flags = 0
        wght_val.ValueNameID = _add_name(font, "Regular")
        wght_val.Value = 400.0
        axis_values.append(wght_val)

        # Italic: Italic
        ital_val = otTables.AxisValue()
        ital_val.Format = 1
        ital_val.AxisIndex = 1
        ital_val.Flags = 0
        ital_val.ValueNameID = _add_name(font, "Italic")
        ital_val.Value = 1.0
        axis_values.append(ital_val)

    elif is_bold:
        # Weight: Bold
        wght_val = otTables.AxisValue()
        wght_val.Format = 1
        wght_val.AxisIndex = 0
        wght_val.Flags = 0
        wght_val.ValueNameID = _add_name(font, "Bold")
        wght_val.Value = 700.0
        axis_values.append(wght_val)

        # Italic: Roman (elidable) with linkedValue to Italic
        ital_val = otTables.AxisValue()
        ital_val.Format = 3  # Format 3 supports LinkedValue
        ital_val.AxisIndex = 1
        ital_val.Flags = 0x0002  # ELIDABLE_AXIS_VALUE_NAME
        ital_val.ValueNameID = _add_name(font, "Roman")
        ital_val.Value = 0.0
        ital_val.LinkedValue = 1.0
        axis_values.append(ital_val)

    else:
        # Regular font
        # Weight: Regular (elidable)
        wght_val = otTables.AxisValue()
        wght_val.Format = 1
        wght_val.AxisIndex = 0
        wght_val.Flags = 0x0002  # ELIDABLE_AXIS_VALUE_NAME
        wght_val.ValueNameID = _add_name(font, "Regular")
        wght_val.Value = 400.0
        axis_values.append(wght_val)

        # Italic: Roman (elidable) with linkedValue to Italic
        ital_val = otTables.AxisValue()
        ital_val.Format = 3  # Format 3 supports LinkedValue
        ital_val.AxisIndex = 1
        ital_val.Flags = 0x0002  # ELIDABLE_AXIS_VALUE_NAME
        ital_val.ValueNameID = _add_name(font, "Roman")
        ital_val.Value = 0.0
        ital_val.LinkedValue = 1.0
        axis_values.append(ital_val)

    stat.AxisValueArray = otTables.AxisValueArray()
    stat.AxisValueArray.AxisValue = axis_values
    stat.AxisValueCount = len(axis_values)
    stat.ElidedFallbackNameID = _add_name(font, "Regular")

    # Add STAT table to font
    from fontTools.ttLib import newTable
    stat_table = newTable("STAT")
    stat_table.table = stat
    font["STAT"] = stat_table

    # Set head.flags bit 3 for hinted fonts (PPEM rounding)
    font["head"].flags |= 0x0008

    font.save(font_path)
    print(f"Added STAT table to {font_path}")


def _add_name(font, name_string):
    """Add a name to the name table and return its ID."""
    name_table = font["name"]
    # Find next available name ID (start from 256 to avoid conflicts)
    existing_ids = {record.nameID for record in name_table.names}

    # Check if name already exists
    for record in name_table.names:
        if record.platformID == 3 and record.platEncID == 1 and record.langID == 0x409:
            try:
                if record.toUnicode() == name_string:
                    return record.nameID
            except:
                pass

    # Find next available ID
    name_id = 256
    while name_id in existing_ids:
        name_id += 1

    # Add name for Windows platform only (no Mac platform to avoid fontbakery warnings)
    name_table.setName(name_string, name_id, 3, 1, 0x409)

    return name_id


if __name__ == "__main__":
    for path in sys.argv[1:]:
        add_stat_table(path)
