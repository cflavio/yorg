local function file_exists(name)
    local f=io.open(name,"r")
    if f~=nil then
        io.close(f)
        return true
    else
        return false
    end
end


local function preinst()
    if file_exists(MojoSetup.destination.."/.mojosetup/mojosetup") then
        MojoSetup.fatal([[You are attempting to overwrite an existing folder; 
if you have a previous installation then uninstall it before installing this 
new one.]])
    end
end


Setup.Package {
    vendor = "ya2.it",
    id = "<name>",
    description = "<Name>",
    version = "<version>",
    write_manifest = true,
    support_uninstall = true,
    preinstall = preinst,
    delete_error_is_fatal = false,
    recommended_destinations = {
        MojoSetup.info.homedir,
        "/opt/games",
        "/usr/local/games"
    },
    Setup.DesktopMenuItem {
        name = "<Name>",
        genericname = "Videogame",
        tooltip = "<Name>",
        icon = "icon.png",
        commandline = "%0/<name>",
        category = "Game",
    },
    Setup.Option {
        value = true,
        required = true,
        bytes = <size>,
        description = "<Name>",
        Setup.File {
            allowoverwrite = true,
            wildcards = {"*"}
        }
    }
}
