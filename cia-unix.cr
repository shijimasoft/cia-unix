require "colorize"

log : File = File.new "cia-unix.log", "w"
log.puts Time.utc.to_s

# dependencies check
tools = ["./ctrtool", "./ctrdecrypt", "./makerom", "seeddb.bin"]
tools.each do |tool|
    case tool
    when "./ctrtool", "./ctrdecrypt", "./makerom"
        if !File.exists? %x[which #{tool}].chomp
            log.delete if File.exists? "cia-unix.log"
            download_dep
            abort "#{tool.lchop("./").colorize.mode(:bold)} not found. Make sure it's located in the #{"same directory".colorize.mode(:underline)}" if !File.exists? tool
        end
    when "seeddb.bin"
        if !File.exists? tool
            log.delete if File.exists? "cia-unix.log"
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
    log.delete if File.exists? "cia-unix.log"
    abort "No #{"CIA".colorize.mode(:bold)}/#{"3DS".colorize.mode(:bold)} roms were found."
end

def check_decrypt(name : String, ext : String)
    if File.exists? "#{name}-decrypted.#{ext}"
        puts "Decryption completed\n".colorize.mode(:underline)
    else
        puts "Decryption failed\n".colorize.mode(:underline)
    end
end

def gen_args(name : String, part_count : Int32) : String
    args : String = ""
    part_count.times do |partition|
        if File.exists? "#{name}.#{partition}.ncch"
            args += "-i '#{name}.#{partition}.ncch:#{partition}:#{partition}' "
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

args : String = ""

# 3ds decrypting
Dir["*.3ds"].each do |ds|
    next if ds.includes? "decrypted"

    args = ""
    i : UInt8 = 0
    dsn : String = ds.chomp ".3ds"

    puts "Decrypting: #{ds.colorize.mode(:bold)}..."
    log.puts %x[./ctrdecrypt '#{ds}']

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
        args += "-i '#{ncch}:#{i}:#{i}' "
    end
    puts "Building decrypted #{dsn} 3DS..."
    log.puts %x[./makerom -f cci -ignoresign -target p -o '#{dsn}-decrypted.3ds' #{args}]
    check_decrypt(dsn, "3ds")
    remove_cache
end

# cia decrypting
Dir["*.cia"].each do |cia|
    next if cia.includes? "decrypted"

    puts "Decrypting: #{cia.colorize.mode(:bold)}..."
    cutn : String = cia.chomp ".cia"
    args = ""
    content = %x[./ctrtool --seeddb=seeddb.bin '#{cia}']

    # game
    if content.match /T.*d.*00040000/
        puts "CIA Type: Game"
        log.puts %x[./ctrdecrypt '#{cia}']
        
        i : UInt8 = 0
        Dir["*.ncch"].sort.each do |ncch|
            args += "-i '#{ncch}:#{i}:#{i}' "
            i += 1
        end
        log.puts %x[./makerom -f cia -ignoresign -target p -o '#{cutn}-decfirst.cia' #{args}]
    # patch
    elsif content.match /T.*d.*0004000(e|E)/
        puts "CIA Type: #{"Patch".colorize.mode(:bold)}"
        log.puts %x[./ctrdecrypt '#{cia}']

        patch_parts : Int32 = Dir["#{cutn}.*.ncch"].size
        args = gen_args(cutn, patch_parts)

        log.puts %x[./makerom -f cia -ignoresign -target p -o '#{cutn} (Patch)-decrypted.cia' #{args}]
        check_decrypt("#{cutn} (Patch)", "cia")
    # dlc
    elsif content.match /T.*d.*0004008(c|C)/
        puts "CIA Type: #{"DLC".colorize.mode(:bold)}"
        log.puts %x[./ctrdecrypt '#{cia}']

        dlc_parts : Int32 = Dir["#{cutn}.*.ncch"].size
        args = gen_args(cutn, dlc_parts)
        
        log.puts %x[./makerom -f cia -dlc -ignoresign -target p -o '#{cutn} (DLC)-decrypted.cia' #{args}]
        check_decrypt("#{cutn} (DLC)", "cia")
    else
        puts "Unsupported CIA"
    end

    Dir["*-decfirst.cia"].each do |decfirst|
        cutn = decfirst.chomp "-decfirst.cia"
    
        puts "Building decrypted #{cutn} CCI..."
        log.puts %x[./makerom -ciatocci '#{decfirst}' -o '#{cutn}-decrypted.cci']
        check_decrypt(cutn, "cci")
    end

    remove_cache
end

log.flush
log.close
puts "Log saved"
