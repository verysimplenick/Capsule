
import bpy, bmesh, random

from mathutils import Vector
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty

from .tk_utils import groups as group_utils
from .tk_utils import select as select_utils
from .export_formats import CAP_ExportFormat
from . import export_presets

#///////////////// - LOCATION DEFAULTS - ///////////////////////////////////////////

class CAP_Add_Path(Operator):
    """Create a new location."""

    bl_idname = "scene.cap_addpath"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        newPath = exp.location_presets.add()
        newPath.name = "Location " + str(len(exp.location_presets))
        newPath.path = ""

        # Position the index to the current location of the
        #count = 0
        #for i, item in enumerate(scn.path_defaults, 1):
            #count += 1

        #oldIndex = scn.path_list_index

        #scn.path_defaults.move(count - 1, scn.path_list_index)
        #scn.path_list_index = oldIndex

        return {'FINISHED'}

class CAP_Delete_Path(Operator):
    """Delete the selected location from the list."""

    bl_idname = "scene.cap_deletepath"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        exp.location_presets.remove(exp.location_presets_listindex)

        return {'FINISHED'}


class CAP_Add_Export(Operator):
    """Create a new file preset."""

    bl_idname = "scene.cap_addexport"
    bl_label = "Add"

    def get_unique_id(self, context, exp):
        newID = random.randrange(0, 1000000)

        for preset in exp.file_presets:
            if preset.instance_id == newID:
                newID = self.get_unique_id(context, exp)

        return newID

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp


        # make the new file preset
        newDefault = exp.file_presets.add()
        newDefault.name = "Export " + str(len(exp.file_presets))
        newDefault.path = ""

        # Ensure the tag index keeps within a window
        exp.file_presets_listindex = len(exp.file_presets) - 1

        return {'FINISHED'}

class CAP_Delete_Export(Operator):
    """Delete the selected file preset from the list."""

    bl_idname = "scene.cap_deleteexport"
    bl_label = "Delete Export Preset"

    #StringProperty(default="Are you sure you wish to delete the selected preset?")

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        if len(exp.file_presets) > 0:
            return True

        return False

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # remove the data from both lists
        exp.file_presets.remove(exp.file_presets_listindex)

        # ensure the selected list index is within the list bounds
        if exp.file_presets_listindex > 0:
            exp.file_presets_listindex -= 1

        return {'FINISHED'}


class CAP_Add_Tag(Operator):
    """Create a new tag."""

    bl_idname = "scene.cap_addtag"
    bl_label = "Add"


    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Add the tag into the main list
        export = exp.file_presets[exp.file_presets_listindex]
        newTag = export.tags.add()
        newTag.name = "Tag " + str(len(export.tags))

        # Now add it for all other passes in the export
        for expPass in export.passes:
            newPassTag = expPass.tags.add()
            newPassTag.name = newTag.name
            newPassTag.index = len(export.tags) - 1

        # Ensure the tag index keeps within a window
        export.tags_index = len(export.tags) - 1

        return {'FINISHED'}

class CAP_Delete_Tag(Operator):
    """Delete the selected tag from the list."""

    bl_idname = "scene.cap_deletetag"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export = exp.file_presets[exp.file_presets_listindex]
        if len(export.tags) > 0:
            currentTag = export.tags[export.tags_index]

            if currentTag.x_user_deletable is True:
                return True

        else:
            return False

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export = exp.file_presets[exp.file_presets_listindex]
        export.tags.remove(export.tags_index)

        for expPass in export.passes:
            expPass.tags_index -= 1
            expPass.tags.remove(export.tags_index)

        if export.tags_index > 0:
            export.tags_index -= 1

        return {'FINISHED'}


class CAP_Add_Pass(Operator):
    """Create a new pass."""

    bl_idname = "scene.cap_addpass"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export = exp.file_presets[exp.file_presets_listindex]
        newPass = export.passes.add()
        newPass.name = "Pass " + str(len(export.passes))
        newPass.path = ""

        # Ensure the new pass has all the current tags
        for tag in export.tags:
            newPassTag = newPass.tags.add()
            newPassTag.name = tag.name
            newPassTag.index = len(export.tags) - 1

        # Ensure the tag index keeps within a window
        export.passes_index = len(export.passes) - 1

        return {'FINISHED'}

class CAP_Delete_Pass(Operator):
    """Delete the selected pass from the list."""

    bl_idname = "scene.cap_deletepass"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export = exp.file_presets[exp.file_presets_listindex]
        if len(export.passes) > 0:
            return True

        return False

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        export = exp.file_presets[exp.file_presets_listindex]
        export.passes.remove(export.passes_index)

        if export.passes_index > 0:
            export.passes_index -= 1

        return {'FINISHED'}

class CAP_Shift_Path_Up(Operator):
    """Move the current entry in the list up by one"""

    bl_idname = "scene.cap_shiftup"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        obj = context.active_object.CAPObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index - 1)
        scn.path_list_index -= 1

        return {'FINISHED'}

class CAP_Shift_Path_Down(Operator):
    """Move the current entry in the list down by one"""

    bl_idname = "scene.cap_shiftdown"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        obj = context.active_object.CAPObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index + 1)
        scn.path_list_index += 1

        return {'FINISHED'}

class CAP_Set_Root_Object(Operator):
    """Allows you to set the Origin Object through an interactive tool.  Right-Click: Select the object you wish to be the origin point for the scene.  Esc - Quit the tool."""

    bl_idname = "scene.cap_setroot"
    bl_label = "Remove"

    def finish(self):
        # This def helps us tidy the shit we started
        # Restore the active area's header to its initial state.
        bpy.context.area.header_text_set()


    def execute(self, context):
        scn = context.scene.CAPScn

        user_preferences = context.user_preferences
        self.addon_prefs = user_preferences.addons[__package__].preferences

        self.groups = []
        self.object = None
        self.list_item = 0
        context.window_manager.modal_handler_add(self)

        # If multi-edit is on, get info from the scene
        if self.addon_prefs.group_multi_edit is True:
            print("Multi-edit on")
            self.object = context.scene.objects.active
            for object in context.selected_objects:
                for foundGroup in object.users_group:
                    self.groups.append(foundGroup)

        # Otherwise, find it in the scene
        else:
            print("Multi-edit off")
            self.list_item = context.scene.CAPScn.group_list_index
            item = context.scene.CAPScn.group_list[context.scene.CAPScn.group_list_index]
            for foundGroup in tk_utils.groups.GetSceneGroups(context.scene, True):
                if foundGroup.name == item.name:
                    self.groups.append(foundGroup)

        print("Groups found....", self.groups)
        self._timer = context.window_manager.event_timer_add(0.05, context.window)
        bpy.ops.object.select_all(action='DESELECT')

        # Set the header text with USEFUL INSTRUCTIONS :O
        context.area.header_text_set(
            "Select the object you want to use as a root object.  " +
            "RMB: Select Collision Object, Esc: Exit"
        )

        return {'RUNNING_MODAL'}

    def modal(self,context,event):
        # If escape is pressed, exit
        if event.type in {'ESC'}:
            self.finish()
            return{'FINISHED'}

        # When an object is selected, set it as a child to the object, and finish.
        elif event.type == 'RIGHTMOUSE':

            # Check only one object was selected
            if context.selected_objects != None and len(context.selected_objects) == 1:
                for group in self.groups:
                    group.CAPGrp.root_object = context.scene.objects.active.name
                if self.object != None:
                    select_utils.FocusObject(self.object)
                else:
                    context.scene.CAPScn.group_list_index = self.list_item
                self.finish()

                return{'FINISHED'}

        return {'PASS_THROUGH'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}


class CAP_Clear_Root_Object(Operator):
    """Clear the currently chosen origin object for the group."""

    bl_idname = "scene.cap_clearroot"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        obj = context.active_object.CAPObj
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        # If multi-edit is on, get info from the scene
        if addon_prefs.group_multi_edit is True:
            print("Multi-edit on")
            for object in context.selected_objects:
                for foundGroup in object.users_group:
                    foundGroup.CAPGrp.root_object = ""

        # Otherwise, find it in the scene
        else:
            print("Multi-edit off")
            item = context.scene.CAPScn.group_list[context.scene.CAPScn.group_list_index]
            for foundGroup in groups.GetSceneGroups(context.scene, True):
                if foundGroup.name == item.name:
                    foundGroup.CAPGrp.root_object = ""

        return {'FINISHED'}


class CAP_Clear_List(Operator):
    """Delete all objects from the export list, and un-mark them for export"""

    bl_idname = "scene.cap_clearlist"
    bl_label = "Delete All"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        objectTab = int(str(scn.list_switch))

        if objectTab == 1:
            for object in context.scene.objects:
                obj = object.CAPObj
                obj.enable_export = False
                obj.in_export_list = False
            scn.object_list.clear()

        elif objectTab == 2:
            for group in group_utils.GetSceneGroups(context.scene, True):
                grp = group.CAPGrp
                grp.enable_export = False
                grp.in_export_list = False
            scn.group_list.clear()

        scn.enable_sel_active = False
        scn.enable_list_active = False

        return {'FINISHED'}

class CAP_Refresh_List(Operator):
    """Rebuild the list based on available objects or groups in the scene."""

    bl_idname = "scene.cap_refreshlist"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        objectTab = int(str(scn.list_switch))

        if objectTab == 1:
            scn.object_list.clear()
            for obj in context.scene.objects:
                if obj.CAPObj.in_export_list is True:
                    entry = scn.object_list.add()
                    entry.name = obj.name
                    entry.prev_name = obj.name
                    entry.enable_export = obj.CAPObj.enable_export


        elif objectTab == 2:
            scn.group_list.clear()
            for group in group_utils.GetSceneGroups(context.scene, True):
                if group.CAPGrp.in_export_list is True:
                        entry = scn.group_list.add()
                        entry.name = group.name
                        entry.prev_name = group.name
                        entry.enable_export = group.CAPGrp.enable_export

        scn.enable_sel_active = False
        scn.enable_list_active = False

        return {'FINISHED'}


class CAP_Reset_Scene(Operator):
    """Reset all object and group variables in the scene.  Use at your own peril!"""

    bl_idname = "scene.cap_resetsceneprops"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        exportedObjects = 0

        # Keep a record of the selected and active objects to restore later
        active = None
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        active = context.active_object

        for group in tk_utils.groups.GetSceneGroups(context.scene, False):
            grp = group.CAPGrp
            grp.enable_export = False
            grp.root_object = ""
            grp.location_default = '0'
            grp.export_default = '0'
            grp.normals = '1'

        for object in context.scene.objects:
            obj = object.CAPObj
            obj.enable_export = False
            obj.use_scene_origin = False
            obj.location_default = '0'
            obj.export_default = '0'
            obj.normals = '1'

        bpy.ops.scene.cap_refobjects()
        bpy.ops.scene.cap_refgroups()

        # Re-select the objects previously selected
        select_utils.FocusObject(active)

        for sel in selected:
            SelectObject(sel)

        return {'FINISHED'}

class CAP_Reset_Defaults(Operator):
    """Reset all location and export defaults in the file"""

    bl_idname = "scene.cap_resetprefs"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        if addon_prefs == None:
            print("ADDON COULD NOT START, CONTACT DEVELOPER FOR ASSISTANCE")
            return

        # Figure out if an object already exists, if yes, DELETE IT
        for object in bpy.data.objects:
            if object.name == addon_prefs.default_datablock:
                DeleteObject(object)

        # Otherwise create the object using the addon preference data
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES')

        defaultDatablock = bpy.context.scene.objects.active
        defaultDatablock.name = addon_prefs.default_datablock
        defaultDatablock.hide = True
        defaultDatablock.hide_render = True
        defaultDatablock.hide_select = True


        return {'FINISHED'}

class CAP_UI_Group_Separate(Operator):
    """Toggle the drop-down menu for separate group export options"""

    bl_idname = "scene.cap_grpseparate"
    bl_label = ""

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        ui = context.scene.CAPUI

        if ui.group_separate_dropdown is True:
            ui.group_separate_dropdown = False
        else:
            ui.group_separate_dropdown = True

        return {'FINISHED'}

class CAP_UI_Group_Options(Operator):
    """Toggle the drop-down menu for separate group export options"""

    bl_idname = "scene.cap_grpoptions"
    bl_label = ""

    def execute(self, context):
        print(self)

        scn = context.scene.CAPScn
        ui = context.scene.CAPUI

        if ui.group_options_dropdown is True:
            ui.group_options_dropdown = False
        else:
            ui.group_options_dropdown = True

        return {'FINISHED'}


class CAP_Refresh_Actions(Operator):
    """Generate a list of groups to browse"""

    bl_idname = "scene.cap_refactions"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        ui = context.scene.CAPUI
        active = context.active_object
        armature = None

        ui.action_list.clear()

        if active.animation_data is not None:
            actions = active.animation_data.nla_tracks
            activeAction = active.animation_data.action

            if activeAction is not None:
                entry = ui.action_list.add()
                entry.name = activeAction.name
                entry.prev_name = activeAction.name
                entry.anim_type = '1'

            for action in actions:
                entry = ui.action_list.add()
                entry.name = action.name
                entry.prev_name = action.name
                entry.anim_type = '2'


        modType = {'ARMATURE'}

        for modifier in active.modifiers:
            if modifier.type in modType:
                armature = modifier.object

        if armature is not None:
            if armature.animation_data is not None:
                actions = armature.animation_data.nla_tracks
                activeAction = armature.animation_data.action

                if activeAction is not None:
                    entry = ui.action_list.add()
                    entry.name = activeAction.name
                    entry.prev_name = activeAction.name
                    entry.anim_type = '3'

                for action in actions:
                    entry = ui.action_list.add()
                    entry.name = action.name
                    entry.prev_name = action.name
                    entry.anim_type = '4'


        return {'FINISHED'}

class CAP_Tutorial_Tags(Operator):
    """Delete the selected file preset from the list."""

    bl_idname = "cap_tutorial.tags"
    bl_label = "Tags let you automatically split objects in your passes by defining an object suffix/prefix and/or object type, that objects in the pass it's used in need to match in order to be included for export, enabiling you to create multiple different versions of an object or group export, without having to manually define them."

    StringProperty(default="Are you sure you wish to delete the selected preset?")

    def execute(self, context):
        print(self)

        #main(self, context)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

        return {'FINISHED'}

class CAP_Create_ExportData(Operator):
    """Create a new empty object for which Capsule data is stored, and where both file presets and other scene data is stored."""

    bl_idname = "cap.exportdata_create"
    bl_label = "Create Capsule Data"

    def execute(self, context):
        print(self)

        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        # Figure out if an object already exists, if yes do nothing
        for object in bpy.data.objects:
            print(object)
            if object.name == addon_prefs.default_datablock:
                self.report({'WARNING'}, "Capsule data for the blend file has been found, a new one will not be created.")
                return {'CANCELLED'}

        # Otherwise create the object using the addon preference data
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES')

        defaultDatablock = bpy.context.scene.objects.active
        defaultDatablock.name = addon_prefs.default_datablock
        defaultDatablock.hide = True
        defaultDatablock.hide_render = True
        defaultDatablock.hide_select = True
        defaultDatablock.CAPExp.is_storage_object = True
        addon_prefs.data_missing = False

        self.report({'INFO'}, "Capsule data created.")
        return {'FINISHED'}


class CAP_Add_Stored_Presets(Operator):
    """Add the currently selected saved preset into the file presets list, enabling it's use for exports in this .blend file."""
    bl_idname = "cap.create_current_preset"
    bl_label = "Default Presets"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        if len(addon_prefs.saved_presets) > 0:
            return True

        else:
            return False

    def execute(self, context):

        # Get the current export data
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Obtain the selected preset
        new_preset = exp.file_presets.add()
        export_presets.CopyPreset(addon_prefs.saved_presets[addon_prefs.saved_presets_index], new_preset)

        return {'FINISHED'}

class CAP_Delete_Presets(Operator):
    """Delete the currently selected saved preset."""
    bl_idname = "cap.delete_global_preset"
    bl_label = "Store Preset"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        if len(addon_prefs.saved_presets) > 0:
            export = addon_prefs.saved_presets[addon_prefs.saved_presets_index]
            
            if export.x_global_user_deletable is True:
                return True

        return False

    def execute(self, context):

        # Get the current export data
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Obtain the selected preset
        addon_prefs.saved_presets.remove(addon_prefs.saved_presets_index)

        # Decrement the list selection
        if addon_prefs.saved_presets_index > 0:
            addon_prefs.saved_presets_index -= 1

        return {'FINISHED'}

class CAP_Store_Presets(Operator):
    """Store the currently selected export preset as a saved preset, to enable it's use in across .blend files."""
    bl_idname = "cap.add_global_preset"
    bl_label = "Store Preset"

    @classmethod
    def poll(cls, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        if len(exp.file_presets) > 0:
            return True

        else:
            return False


    def execute(self, context):

        # Get the current export data
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        exp = bpy.data.objects[addon_prefs.default_datablock].CAPExp

        # Obtain the selected preset
        new_preset = addon_prefs.saved_presets.add()
        export_presets.CopyPreset(exp.file_presets[exp.file_presets_listindex], new_preset)

        return {'FINISHED'}


