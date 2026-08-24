/* Union assembly of "calibration sample" used in round-robin Bragg-edge imaging
   experiments, see publication

   Ramadhan, R.S. et al. (2026). Preliminary Campaign of Bragg Edge Neutron Imaging Round Robin. 
   In: Craft, A.E., Bilheux, H.Z. (eds) Proceedings of the 12th World Conference on Neutron Radiography. WCNR 2024. Springer Proceedings in Physics, vol 348. Springer, Cham. 
   https://doi.org/10.1007/978-3-032-15003-5_44

   Original model assembled by Mads Bertelsen, ESS - for use in this model it has been scaled down a factor of 4 in size. 
*/

COMPONENT init = Union_init()
AT (0, 0, 0) ABSOLUTE

COMPONENT Al_inc = Incoherent_process(
 sigma = 0.0328, unit_cell_volume = 66.4)
AT (0, 0, 0) ABSOLUTE

COMPONENT Al_pow = Powder_process(
 reflections = "Al.laz")
AT (0, 0, 0) ABSOLUTE

COMPONENT Al = Union_make_material(
 process_string = "Al_inc,Al_pow", my_absorption = 1.391566265060241)
AT (0, 0, 0) ABSOLUTE

COMPONENT Cu_inc = Incoherent_process(
 sigma = 2.2, unit_cell_volume = 47.24)
AT (0, 0, 0) ABSOLUTE

COMPONENT Cu_pow = Powder_process(
 reflections = "Cu.laz")
AT (0, 0, 0) ABSOLUTE

COMPONENT Cu = Union_make_material(
 process_string = "Cu_inc,Cu_pow", my_absorption = 32.00677392040643)
AT (0, 0, 0) ABSOLUTE

COMPONENT Ni_inc = Incoherent_process(
 sigma = 20.8, unit_cell_volume = 43.76)
AT (0, 0, 0) ABSOLUTE

COMPONENT Ni_pow = Powder_process(
 reflections = "Ni.laz")
AT (0, 0, 0) ABSOLUTE

COMPONENT Ni = Union_make_material(
 process_string = "Ni_inc,Ni_pow", my_absorption = 41.04204753199269)
AT (0, 0, 0) ABSOLUTE

COMPONENT Ti_inc = Incoherent_process(
 sigma = 5.74, unit_cell_volume = 35.33)
AT (0, 0, 0) ABSOLUTE

COMPONENT Ti_pow = Powder_process(
 reflections = "Ti.laz")
AT (0, 0, 0) ABSOLUTE

COMPONENT Ti = Union_make_material(
 process_string = "Ti_inc,Ti_pow", my_absorption = 34.474950467025195)
AT (0, 0, 0) ABSOLUTE

COMPONENT Pb_inc = Incoherent_process(
 sigma = 0.012, unit_cell_volume = 121.29)
AT (0, 0, 0) ABSOLUTE

COMPONENT Pb_pow = Powder_process(
 reflections = "Pb.laz")
AT (0, 0, 0) ABSOLUTE

COMPONENT Pb = Union_make_material(
 process_string = "Pb_inc,Pb_pow", my_absorption = 0.5606397889356088)
AT (0, 0, 0) ABSOLUTE

COMPONENT Fe_inc = Incoherent_process(
 sigma = 0.8, unit_cell_volume = 24.04)
AT (0, 0, 0) ABSOLUTE

COMPONENT Fe_pow = Powder_process(
 reflections = "Fe.laz")
AT (0, 0, 0) ABSOLUTE

COMPONENT Fe = Union_make_material(
 process_string = "Fe_inc,Fe_pow", my_absorption = 21.297836938435942)
AT (0, 0, 0) ABSOLUTE

COMPONENT B4C_inc = Incoherent_process(
 sigma = 6.801, unit_cell_volume = 328.9)
AT (0, 0, 0) ABSOLUTE

COMPONENT B4C_pow = Powder_process(
 reflections = "B4C.laz")
AT (0, 0, 0) ABSOLUTE

COMPONENT B4C = Union_make_material(
 process_string = "B4C_inc,B4C_pow", my_absorption = 84)
AT (0, 0, 0) ABSOLUTE

COMPONENT base_cyl = Union_cylinder(
 material_string = "Al", priority = 100,
 radius = 0.04/4.0, yheight = 0.05/4.0)
AT (0, 0, 0) RELATIVE Goniometer

COMPONENT Cu_cyl = Union_cylinder(
 material_string = "Cu", priority = 150,
 radius = 0.007/4.0, yheight = 0.046/4.0)
AT (0.03/4.0, 0, 0.0) RELATIVE base_cyl

COMPONENT Ni_cyl = Union_cylinder(
 material_string = "Ni", priority = 151,
 radius = 0.007/4.0, yheight = 0.046/4.0)
AT (0.02427/4.0, 0, 0.01763/4.0) RELATIVE base_cyl

COMPONENT Ti_cyl = Union_cylinder(
 material_string = "Ti", priority = 152,
 radius = 0.007/4.0, yheight = 0.046/4.0)
AT (0.00927/4.0, 0, 0.02853/4.0) RELATIVE base_cyl

COMPONENT Pb_cyl = Union_cylinder(
 material_string = "Pb", priority = 153,
 radius = 0.007/4.0, yheight = 0.046/4.0)
AT (-0.00927/4.0, 0, 0.02853/4.0) RELATIVE base_cyl

COMPONENT Fe_cyl = Union_cylinder(
 material_string = "Fe", priority = 154,
 radius = 0.007/4.0, yheight = 0.046/4.0)
AT (-0.02427/4.0, 0, 0.01763/4.0) RELATIVE base_cyl

COMPONENT B4C_cyl = Union_cylinder(
 material_string = "B4C", priority = 155,
 radius = 0.007/4.0, yheight = 0.046/4.0)
AT (-0.03/4.0, 0, 0.0) RELATIVE base_cyl

/* The loggers below give insight into the scattering
   within the union assembly. */
/*COMPONENT logger_space_zx_all = Union_logger_2D_space(
 D_direction_1 = "z", D1_min = -0.05/4.0,
 D1_max = 0.05/4.0, n1 = 1000,
 D_direction_2 = "x", D2_min = -0.05/4.0,
 D2_max = 0.05/4.0, n2 = 1000,
 filename = "space_zx.dat")
AT (0, 0, 0) RELATIVE Goniometer

COMPONENT logger_space_zy_all = Union_logger_2D_space(
 D_direction_1 = "z", D1_min = -0.05/4.0,
 D1_max = 0.05/4.0, n1 = 1000,
 D_direction_2 = "y", D2_min = -0.05/4.0,
 D2_max = 0.05/4.0, n2 = 1000,
 filename = "space_zy.dat")
AT (0, 0, 0) RELATIVE Goniometer

COMPONENT logger_space_xy_all = Union_logger_2D_space(
 D_direction_1 = "x", D1_min = -0.05/4.0,
 D1_max = 0.05/4.0, n1 = 1000,
 D_direction_2 = "y", D2_min = -0.05/4.0,
 D2_max = 0.05/4.0, n2 = 1000,
 filename = "space_xy.dat")
 AT (0, 0, 0) RELATIVE Goniometer */

