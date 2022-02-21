require "colorize"

log : File = File.open "log.txt", "w"
log.puts Time.utc.to_s

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

Dir["*.cia"].each do |cia|
    if cia.includes? "decrypted"
        next
    end

    puts "Decrypting: #{cia.colorize.mode(:bold)}..."
    cutn : String = cia.chomp ".cia"
    args : String = ""
    content = %x[./ctrtool -tmd '#{cia}']

    if content.match /T.*D.*00040000/
        puts "CIA Type: Game"
        log.puts %x[python2.7 decrypt.py '#{cia}']
        
        i : UInt8 = 0
        Dir["*.ncch"].each do |ncch|
            args += "-i '#{ncch}:#{i}:#{i}' "
            i += 1
        end
        log.puts %x[./makerom -f cia -ignoresign -target p -o '#{cutn}-decfirst.cia' #{args}]
        
    elsif content.match /T.*D.*0004000E/
        puts "CIA Type: #{"Patch".colorize.mode(:bold)}"
        log.puts %x[python2.7 decrypt.py '#{cia}']

        patch_parts : Int32 = Dir["#{cutn}.*.ncch"].size
        args = gen_args(cutn, patch_parts)

        log.puts %x[./makerom -f cia -ignoresign -target p -o '#{cutn} (Patch)-decrypted.cia' #{args}]
        check_decrypt("#{cutn} (Patch)", "cia")

    elsif content.match /T.*D.*0004008C/
        puts "CIA Type: #{"DLC".colorize.mode(:bold)}"
        log.puts %x[python2.7 decrypt.py '#{cia}']

        dlc_parts : Int32 = Dir["#{cutn}.*.ncch"].size
        args = gen_args(cutn, dlc_parts)
        
        log.puts %x[./makerom -f cia -dlc -ignoresign -target p -o '#{cutn} (DLC)-decrypted.cia' #{args}]
        check_decrypt("#{cutn} (DLC)", "cia")
    else
        abort "Unsupported CIA"
    end
end

Dir["*-decfirst.cia"].each do |decfirst|
    cutn : String = decfirst.chomp "-decfirst.cia"

    puts "Building decrypted #{cutn} CCI..."
    log.puts %x[./makerom -ciatocci '#{decfirst}' -o '#{cutn}-decrypted.cci']
    check_decrypt(cutn, "cci")
end

# cleanup
Dir["*-decfirst.cia"].each do |fname| File.delete(fname) end
Dir["*.ncch"].each do |fname| File.delete(fname) end

log.close