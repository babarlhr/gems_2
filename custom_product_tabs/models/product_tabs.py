# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    # General
    primary_use = fields.Char(string="Primary Use")
    moc_primary = fields.Char(string="MOC Primary")
    moc_secondary = fields.Char(string="MOC Secondary")
    moc_details = fields.Char(string="MOC Details")
    general_weight = fields.Float(string="Weight (Unpackaged) (Kg)")
    inner_diameter = fields.Float(string="Inner Diameter (mm)")
    outer_diameter = fields.Float(string="Outer Diameter (mm)")
    general_length = fields.Float(string="Length (mm)")
    general_width = fields.Float(string="Width (mm)")
    general_height = fields.Float(string="Height (mm)")
    connection_type = fields.Char(string="Connection Type")
    connection_moc = fields.Char(string="Connection MOC")
    reducer_from = fields.Float(string="From (mm)")
    reducer_to = fields.Float(string="To (mm)")
    general_specs = fields.Text(string="Specifications")

    # Process
    feed_composition = fields.Char(string="Feed Composition")
    qin_phase = fields.Selection([
        ('gas', 'Gas (g)'),
        ('liquid', 'Liquid (aq)'),
        ('solid', 'Solid (s)'),
        ('slurry', 'Slurry (aq-s)'),
        ('sludge', 'Sludge (s-aq)')
    ], string="Qin Phase")
    flow_operating = fields.Float(string="Operating (Qop) (m3/h)")
    flow_max = fields.Float(string="Maximum (Qmax) (m3/h)")
    flow_min = fields.Float(string="Minimum (Qmin) (m3/h)")
    pressure_operating = fields.Float(string="Operating (Pop) (bar)")
    pressure_max = fields.Float(string="Maximum (Pmax) (bar)")
    pressure_min = fields.Float(string="Minimum (Pmin) (bar)")
    cont_pressure_rating = fields.Float(string="Minimum (Pmin) (bar)")
    motors = fields.Selection([
        ('manual', 'Manual'),
        ('auto_electrical', 'Auto Electrical'),
        ('auto_pneumatic', 'Auto Pneumatic'),
        ('auto_other', 'Auto Other')
    ], string="Motors")
    motor_desc = fields.Char(string="Motor Descp.")
    valves = fields.Selection([
        ('manual', 'Manual'),
        ('automatic', 'Automatic')
    ], string="Valves/Meters")
    valves_desc = fields.Char(string="Valves/Meters Description")
    process_specs = fields.Char(string="Specifications")

    # Electrical
    power = fields.Selection([
        ('input', 'Input'),
        ('output', 'Output')
    ], string="Power")
    power_actual_kw = fields.Float(string="Power (KW)")
    power_actual_kva = fields.Float(string="Power (KvA)")
    power_rating_volt = fields.Float(string="Power Rating (V)")
    power_rating_phase = fields.Float(string="Power (Phase)")
    power_rating_hertz = fields.Float(string="Power (Hz)")
    cooling_specs = fields.Char(string="Cooling Specification")
    atex_rating = fields.Char(string="ATEX Rating")
    cable_conn_size = fields.Float(string="Connection Size (mm)")
    cable_gland_spec = fields.Float(string="Gland Specification (mm)")
    cable_spec = fields.Char(string="Specification")
    cable_length = fields.Float(string="Length (mm)")
    cable_armoured = fields.Char(string="Armoured")
    cable_description = fields.Char(string="Description")
    power_specs = fields.Char(string="Specification")

    # Instrumentation & Control
    ic_measure_param = fields.Char(string="Measurement Parameter")
    ic_control_type = fields.Char(string="Control Type")
    ic_communication = fields.Selection([
        ('wired', 'Wired'),
        ('wireless', 'Wireless')
    ], string="Communication")
    ic_communication_desc = fields.Char(string="Description")
    ic_material_interface = fields.Selection([
        ('contact', 'Contact'),
        ('radar', 'Radar'),
        ('other', 'Other')
    ], string="Material Interface")
    ic_material_interface_desc = fields.Char(string="Decription")
    ic_power_supply = fields.Selection([
        ('battery', 'Battery'),
        ('power_supply', 'Power Supply')
    ], string="Power Supply")
    ic_specs = fields.Text(string="Specifications")

    # Packaging
    package_type = fields.Selection([
        ('drum', 'Drum'),
        ('jumbo_bag', 'Jumbo Bag'),
        ('box', 'Box'),
        ('container', 'Container'),
        ('ibc', 'IBC'),
        ('ship_cont_20', 'Shipping Container 20ft'),
        ('ship_cont_40', 'Shipping Container 40ft'),
        ('other', 'Other')
    ], string="Package Type")
    package_desc = fields.Char(string="Packaging Decription")
    package_length = fields.Float(string="Length (mm)")
    package_width = fields.Float(string="Width (mm)")
    package_height = fields.Float(string="Height (mm)")
    package_weight = fields.Float(string="Packaged Weight (Kg)")
    package_specs = fields.Text(string="Specifications")
