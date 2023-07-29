bl_info = {
    "name": "Armature Layer Selection",
    "blender": (3, 6, 0),
    "category": "Rigging",
}

import bpy

class ArmatureLayerProperties(bpy.types.PropertyGroup):
    for i in range(32):
        exec(f"""
layer_name_{i}: bpy.props.StringProperty(name="Layer {i+1}")
layer_number_{i}: bpy.props.IntProperty(name="Layer Number {i+1}", min=1, max=32)
""")
    layer_count: bpy.props.IntProperty(name="Layer Count", default=1, min=1, max=32)

class ArmatureLayerPanel(bpy.types.Panel):
    bl_label = "Armature Layers"
    bl_idname = "OBJECT_PT_armature_layer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        props = context.object.armature_layer_props
        armature = context.object.data

        for i in range(props.layer_count):
            row = layout.row(align=True)
            row.prop(props, f"layer_name_{i}", text="")
            row.prop(props, f"layer_number_{i}", text="")
            row.operator("object.move_armature_layer_up", text="", icon='TRIA_UP').layer_index = i
            row.operator("object.move_armature_layer_down", text="", icon='TRIA_DOWN').layer_index = i
            row.operator("object.remove_armature_layer", text="", icon='X').layer_index = i
            layer_number = getattr(props, f"layer_number_{i}") - 1
            if armature.layers[layer_number]:
                row.operator("object.deactivate_armature_layer", text="Hide").layer_index = i
            else:
                row.operator("object.activate_armature_layer", text="Show").layer_index = i

        if props.layer_count < 32:
            layout.operator("object.add_armature_layer", text="Add Layer")

class ActivateArmatureLayerOperator(bpy.types.Operator):
    bl_idname = "object.activate_armature_layer"
    bl_label = "Activate Armature Layer"
    layer_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        props = context.object.armature_layer_props
        armature = context.object.data
        layer_number = getattr(props, f"layer_number_{self.layer_index}") - 1
        armature.layers[layer_number] = True
        return {'FINISHED'}

class DeactivateArmatureLayerOperator(bpy.types.Operator):
    bl_idname = "object.deactivate_armature_layer"
    bl_label = "Deactivate Armature Layer"
    layer_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        props = context.object.armature_layer_props
        armature = context.object.data
        layer_number = getattr(props, f"layer_number_{self.layer_index}") - 1
        armature.layers[layer_number] = False
        return {'FINISHED'}

class AddArmatureLayerOperator(bpy.types.Operator):
    bl_idname = "object.add_armature_layer"
    bl_label = "Add Armature Layer"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        props = context.object.armature_layer_props
        props.layer_count += 1
        return {'FINISHED'}

class RemoveArmatureLayerOperator(bpy.types.Operator):
    bl_idname = "object.remove_armature_layer"
    bl_label = "Remove Armature Layer"
    layer_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        props = context.object.armature_layer_props
        if props.layer_count > 1:  # Must leave at least one layer
            for i in range(self.layer_index, props.layer_count - 1):
                setattr(props, f"layer_name_{i}", getattr(props, f"layer_name_{i+1}"))
                setattr(props, f"layer_number_{i}", getattr(props, f"layer_number_{i+1}"))
            props.layer_count -= 1
        return {'FINISHED'}

class MoveArmatureLayerUpOperator(bpy.types.Operator):
    bl_idname = "object.move_armature_layer_up"
    bl_label = "Move Armature Layer Up"
    layer_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        props = context.object.armature_layer_props
        if self.layer_index > 0:  # Can't move the first layer up
            # Swap this layer with the one above it
            name_temp = getattr(props, f"layer_name_{self.layer_index - 1}")
            number_temp = getattr(props, f"layer_number_{self.layer_index - 1}")
            setattr(props, f"layer_name_{self.layer_index - 1}", getattr(props, f"layer_name_{self.layer_index}"))
            setattr(props, f"layer_number_{self.layer_index - 1}", getattr(props, f"layer_number_{self.layer_index}"))
            setattr(props, f"layer_name_{self.layer_index}", name_temp)
            setattr(props, f"layer_number_{self.layer_index}", number_temp)
        return {'FINISHED'}

class MoveArmatureLayerDownOperator(bpy.types.Operator):
    bl_idname = "object.move_armature_layer_down"
    bl_label = "Move Armature Layer Down"
    layer_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        props = context.object.armature_layer_props
        if self.layer_index < props.layer_count - 1:  # Can't move the last layer down
            # Swap this layer with the one below it
            name_temp = getattr(props, f"layer_name_{self.layer_index + 1}")
            number_temp = getattr(props, f"layer_number_{self.layer_index + 1}")
            setattr(props, f"layer_name_{self.layer_index + 1}", getattr(props, f"layer_name_{self.layer_index}"))
            setattr(props, f"layer_number_{self.layer_index + 1}", getattr(props, f"layer_number_{self.layer_index}"))
            setattr(props, f"layer_name_{self.layer_index}", name_temp)
            setattr(props, f"layer_number_{self.layer_index}", number_temp)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ArmatureLayerProperties)
    bpy.types.Object.armature_layer_props = bpy.props.PointerProperty(type=ArmatureLayerProperties)
    bpy.utils.register_class(ArmatureLayerPanel)
    bpy.utils.register_class(ActivateArmatureLayerOperator)
    bpy.utils.register_class(DeactivateArmatureLayerOperator)
    bpy.utils.register_class(AddArmatureLayerOperator)
    bpy.utils.register_class(RemoveArmatureLayerOperator)
    bpy.utils.register_class(MoveArmatureLayerUpOperator)
    bpy.utils.register_class(MoveArmatureLayerDownOperator)

def unregister():
    bpy.utils.unregister_class(ArmatureLayerProperties)
    del bpy.types.Object.armature_layer_props
    bpy.utils.unregister_class(ArmatureLayerPanel)
    bpy.utils.unregister_class(ActivateArmatureLayerOperator)
    bpy.utils.unregister_class(DeactivateArmatureLayerOperator)
    bpy.utils.unregister_class(AddArmatureLayerOperator)
    bpy.utils.unregister_class(RemoveArmatureLayerOperator)
    bpy.utils.unregister_class(MoveArmatureLayerUpOperator)
    bpy.utils.unregister_class(MoveArmatureLayerDownOperator)

    