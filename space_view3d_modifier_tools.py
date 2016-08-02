# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# by meta-androcto, saidenka #

bl_info = {
    "name": "Modifier Tools",
    "author": "Meta Androcto, saidenka",
    "version": (0, 2, 1),
    "blender": (2, 77, 0),
    "location": "Properties > Modifiers",
    "description": "Modifiers Specials Show/Hide/Apply Selected",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6"
    "/Py/Scripts",
    "tracker_url": "https://developer.blender.org/maniphest/project/3/type/Bug/",
    "category": "3D View"
        }

import bpy


class ApplyAllModifiers(bpy.types.Operator):
    bl_idname = "object.apply_all_modifiers"
    bl_label = "Apply All"
    bl_description = "Apply All modifiers of the selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        is_select, is_mod = False, False
        message_a, message_b = "", ""

        for obj in bpy.context.selected_objects:
            is_select = True

            # copying context for the operator's override
            contx = bpy.context.copy()
            contx['object'] = obj

            for mod in obj.modifiers[:]:
                contx['modifier'] = mod
                is_mod = True
                try:
                    bpy.ops.object.modifier_apply(contx, apply_as='DATA',
                                                  modifier=contx['modifier'].name)
                except:
                    message_b = "Applying modifiers has failed for some objects"
                    continue

        if is_select:
            if is_mod:
                message_a = "Applying modifiers on all Selected Objects"
            else:
                message_a = "No Modifiers on Selected Objects"
        else:
            self.report(type={"INFO"}, message="No Selection. No changes applied")
            return {'CANCELLED'}

        self.report(type={"INFO"}, message=(message_a if not message_b else message_b))

        return {'FINISHED'}


class DeleteAllModifiers(bpy.types.Operator):
    bl_idname = "object.delete_all_modifiers"
    bl_label = "Remove All"
    bl_description = "Remove All modifiers of the selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        is_select, is_mod = False, False
        message_a = ""

        for obj in context.selected_objects:
            is_select = True
            modifiers = obj.modifiers[:]
            for modi in modifiers:
                is_mod = True
                obj.modifiers.remove(modi)

        if is_select:
            if is_mod:
                message_a = "Removing modifiers on all Selected Objects"
            else:
                message_a = "No Modifiers on Selected Objects"
        else:
            self.report(type={"INFO"}, message="No Selection. No changes applied")
            return {'CANCELLED'}

        self.report(type={"INFO"}, message=message_a)
        return {'FINISHED'}


class ToggleApplyModifiersView(bpy.types.Operator):
    bl_idname = "object.toggle_apply_modifiers_view"
    bl_label = "Hide Viewport"
    bl_description = "Shows/Hide modifier of the selected object(s) in 3d View"
    bl_options = {'REGISTER'}

    def execute(self, context):
        is_apply = True
        message_a = ""

        for mod in context.active_object.modifiers:
            if (mod.show_viewport):
                is_apply = False
                break
        for obj in context.selected_objects:
            for mod in obj.modifiers:
                mod.show_viewport = is_apply

        if is_apply:
            message_a = "Applying modifiers to view"
        else:
            message_a = "Unregistered modifiers apply to the view"

        self.report(type={"INFO"}, message=message_a)
        return {'FINISHED'}


class ToggleAllShowExpanded(bpy.types.Operator):
    bl_idname = "wm.toggle_all_show_expanded"
    bl_label = "Expand/Collapse All"
    bl_description = "Expand/Collapse Modifier Stack"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.active_object
        if (len(obj.modifiers)):
            vs = 0
            for mod in obj.modifiers:
                if (mod.show_expanded):
                    vs += 1
                else:
                    vs -= 1
            is_close = False
            if (0 < vs):
                is_close = True
            for mod in obj.modifiers:
                mod.show_expanded = not is_close
        else:
            self.report(type={'WARNING'}, message="Not a single modifier")
            return {'CANCELLED'}

        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


# Menu #
def menu(self, context):

    if (context.active_object):
        if (len(context.active_object.modifiers)):
            col = self.layout.column(align=True)

            row = col.row(align=True)
            row.operator(ApplyAllModifiers.bl_idname,
                         icon='IMPORT', text="Apply All")
            row.operator(DeleteAllModifiers.bl_idname,
                         icon='X', text="Delete All")

            row = col.row(align=True)
            row.operator(ToggleApplyModifiersView.bl_idname,
                         icon='RESTRICT_VIEW_OFF',
                         text="Viewport Vis")
            row.operator(ToggleAllShowExpanded.bl_idname,
                         icon='FULLSCREEN_ENTER',
                         text="Toggle Stack")


def register():
    bpy.utils.register_module(__name__)

    # Add "Specials" menu to the "Modifiers" menu
    bpy.types.DATA_PT_modifiers.prepend(menu)


def unregister():
    bpy.types.DATA_PT_modifiers.remove(menu)

    # Remove "Specials" menu from the "Modifiers" menu.
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
