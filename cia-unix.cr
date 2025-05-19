require "colorize"

LOG = File.new "cia-unix.log", "w"
LOG.puts Time.utc.to_s

# dependencies check
tools = ["./ctrtool", "./ctrdecrypt", "./makerom", "seeddb.bin"]
tools.each do |tool|
    case tool
    when "./ctrtool", "./ctrdecrypt", "./makerom"
        if !File.exists? %x[which #{tool}].chomp
            LOG.delete if File.exists? "cia-unix.log"
            download_dep
            abort "#{tool.lchop("./").colorize.mode(:bold)} not found. Make sure it's located in the #{"same directory".colorize.mode(:underline)}" if !File.exists? tool
        end
    when "seeddb.bin"
        if !File.exists? tool
            LOG.delete if File.exists? "cia-unix.log"
            download_dep
            abort "#{tool.colorize.mode(:bold)} not found. Make sure it's located in the #{"same directory".colorize.mode(:underline)}" if !File.exists? tool
        end
    end
end

def download_dep
    print "Some #{"tools".colorize.mode(:bold)} are missing, do you want to download them? (y/n): "
    if ["y", "Y"].includes? gets.to_s
        system "./dltools.sh"
    end 
end

# roms presence check
if Dir["*.cia"].size.zero? && Dir["*.3ds"].size.zero?
    LOG.delete if File.exists? "cia-unix.log"
    abort "No #{"CIA".colorize.mode(:bold)}/#{"3DS".colorize.mode(:bold)} roms were found."
end

def run_tool(name : String, args : Array(String)) : String
    process = Process.new("./#{name}", args: args, output: Process::Redirect::Pipe)
    content = process.output.gets_to_end
    LOG.puts content
    exit_code = process.wait.exit_code
    raise "#{name} failed with exit code #{exit_code}" if exit_code != 0
    content
end

def check_decrypt(name : String, ext : String)
    if File.exists? "#{name}-decrypted.#{ext}"
        puts "Decryption completed\n".colorize.mode(:underline)
    else
        puts "Decryption failed\n".colorize.mode(:underline)
    end
end

def gen_args(name : String, part_count : Int32) : Array(String)
    args = [] of String
    part_count.times do |partition|
        if File.exists? "#{name}.#{partition}.ncch"
            args += ["-i", "#{name}.#{partition}.ncch:#{partition}:#{partition}"]
        end
    end
    return args
end

# cache cleanup
def remove_cache
    puts "Removing cache..."
    Dir["*-decfirst.cia"].each do |fname| File.delete(fname) end
    Dir["*.ncch"].each do |fname| File.delete(fname) end
end

# 3ds decrypting
Dir["*.3ds"].each do |ds|
    next if ds.includes? "decrypted"

    i : UInt8 = 0
    dsn : String = ds.chomp ".3ds"
    args = ["-f", "cci", "-ignoresign", "-target", "p", "-o", "#{dsn}-decrypted.3ds"]

    puts "Decrypting: #{ds.colorize.mode(:bold)}..."
    run_tool("ctrdecrypt", [ds])

    Dir["#{dsn}.*.ncch"].each do |ncch|
        case ncch
        when "#{dsn}.Main.ncch"
            i = 0
        when "#{dsn}.Manual.ncch"
            i = 1
        when "#{dsn}.DownloadPlay.ncch"
            i = 2
        when "#{dsn}.Partition4.ncch"
            i = 3
        when "#{dsn}.Partition5.ncch"
            i = 4
        when "#{dsn}.Partition6.ncch"
            i = 5
        when "#{dsn}.N3DSUpdateData.ncch"
            i = 6
        when "#{dsn}.UpdateData.ncch"
            i = 7 
        end
        args += ["-i", "#{ncch}:#{i}:#{i}"]
    end
    puts "Building decrypted #{dsn} 3DS..."
    run_tool("makerom", args)
    check_decrypt(dsn, "3ds")
    remove_cache
end

# cia decrypting
Dir["*.cia"].each do |cia|
    next if cia.includes? "decrypted"

    puts "Decrypting: #{cia.colorize.mode(:bold)}..."
    cutn : String = cia.chomp ".cia"
    content = run_tool("ctrtool", ["--seeddb=seeddb.bin", cia])

    # game
    if content.match /T.*d.*00040000/
        puts "CIA Type: Game"
        run_tool("ctrdecrypt", [cia])

        args = ["-f", "cia", "-ignoresign", "-target", "p", "-o", "#{cutn}-decfirst.cia"]
        i : UInt8 = 0
        Dir["*.ncch"].sort.each do |ncch|
            args += ["-i", "#{ncch}:#{i}:#{i}"]
            i += 1
        end
        run_tool("makerom", args)
    # patch
    elsif content.match /T.*d.*0004000(e|E)/
        puts "CIA Type: #{"Patch".colorize.mode(:bold)}"
        run_tool("ctrdecrypt", [cia])

        args = ["-f", "cia", "-ignoresign", "-target", "p", "-o", "#{cutn} (Patch)-decrypted.cia"]
        patch_parts : Int32 = Dir["#{cutn}.*.ncch"].size
        args += gen_args(cutn, patch_parts)

        run_tool("makerom", args)
        check_decrypt("#{cutn} (Patch)", "cia")
    # dlc
    elsif content.match /T.*d.*0004008(c|C)/
        puts "CIA Type: #{"DLC".colorize.mode(:bold)}"
        run_tool("ctrdecrypt", [cia])

        args = ["-f", "cia", "-dlc", "-ignoresign", "-target", "p", "-o", "#{cutn} (DLC)-decrypted.cia"]
        dlc_parts : Int32 = Dir["#{cutn}.*.ncch"].size
        args += gen_args(cutn, dlc_parts)

        run_tool("makerom", args)
        check_decrypt("#{cutn} (DLC)", "cia")
    else
        puts "Unsupported CIA"
    end

    Dir["*-decfirst.cia"].each do |decfirst|
        cutn = decfirst.chomp "-decfirst.cia"
    
        puts "Building decrypted #{cutn} CCI..."
        run_tool("makerom", ["-ciatocci", decfirst, "-o", "#{cutn}-decrypted.cci"])
        check_decrypt(cutn, "cci")
    end

    remove_cache
end

LOG.flush
LOG.close
puts "Log saved"
