![DIADEM banner](../images/toplogo-diadem.png)
# <img src="../../images/Under_Construction_small.png" alt="under construction" align="middle"> <img src="../../images/brainhelmet_small.png" alt="Si-brain helmet construction" align="middle"> <img src="../../images/panraid_small.png" alt="PaNRAID logo" align="middle"> PaNRAID Software Issues / Workarounds <img src="../../images/panraid_small.png" alt="PaNRAID logo" align="middle"> <img src="../../images/brainhelmet_small.png" alt="Si-brain helmet construction" align="middle"> <img src="../../images/Under_Construction_small.png" alt="under construction" align="middle">

### -—> Work in progress! Subject to change! <—- 

_Work and tutorials during PaNRAID is based on open source software + optional NVIDIA infrastructure_

# macOS

## Issue 1: Mismatch between macOS SDK version and `panraid` env:

```bash
ld: warning: ignoring file /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib/libSystem.tbd, malformed file
/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib/libSystem.tbd:4:20: error: unknown architecture
                   arm64e.x1-macos, arm64e.x1-maccatalyst ]
                   ^~~~~~~~~~~~~~~

ld: warning: ignoring file /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib/libm.tbd, malformed file
/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib/libm.tbd:4:20: error: unknown architecture
                   arm64e.x1-macos, arm64e.x1-maccatalyst ]
                   ^~~~~~~~~~~~~~~

Undefined symbols for architecture arm64:
  "___error", referenced from:
      _main in cc-370876.o
      _mcparm_double in cc-370876.o
  "___sincos_stret", referenced from:
      _mcdis_Circle in cc-370876.o
      __randvec_target_circle in cc-370876.o
      _init in cc-370876.o
      _raytrace in cc-370876.o
      _class_Monochromator_flat_trace in cc-370876.o
  "___sprintf_chk", referenced from:
```

## Workaround 1:

Use

```bash
export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk/
```

in your environment.
