function ConnStatus(n)
    local status = wifi.sta.status()
    local x = n+1
    if (x < 50) and ( status < 5 ) then
        tmr.alarm(0,100,0,function() ConnStatus(x) end)
    else
        if status == 5 then
            print("Connected as "..wifi.sta.getip())
        else
            print("Connection failed :(")
        end
    end
end

wifi.setmode(wifi.STATION)
wifi.sta.config("SSID","XXXXXXXX")
print("Connecting to wifi")
ConnStatus(0)

id=0
sda=4
scl=5

i2c.setup(id,sda,scl,i2c.SLOW)

function read_reg(dev_addr, reg_addr)
    i2c.start(id)
    i2c.address(id, dev_addr ,i2c.TRANSMITTER)
    i2c.write(id,reg_addr)
    i2c.stop(id)
    i2c.start(id)
    i2c.address(id, dev_addr,i2c.RECEIVER)
    c=i2c.read(id,1)
    i2c.stop(id)
    return c
end

function write_reg(dev_addr, reg_addr, reg_val)
    i2c.start(id)
    i2c.address(id, dev_addr, i2c.TRANSMITTER)
    i2c.write(id, reg_addr)
    i2c.write(id, reg_val)
    i2c.stop(id)
end

L3GD20addr=0x6A
L3GD20lowODR=0x39
L3GD20CTRL4=0x23
L3GD20CTRL1=0x20
L3GD20OUTXL=0x28
L3GD20OUTXH=0x29
L3GD20OUTYL=0x2A
L3GD20OUTYH=0x2B
L3GD20OUTZL=0x2C
L3GD20OUTZH=0x2D

write_reg(L3GD20addr,L3GD20lowODR,0x01)
write_reg(L3GD20addr,L3GD20CTRL4,0x00)
write_reg(L3GD20addr,L3GD20CTRL1,0x8F)

L3GD20items=100

function readL3GD20()
    if string.byte(read_reg(L3GD20addr,0x27)) > 7 then
        if L3GD20list.items > 100 then
            List.pop(L3GD20list)
            List.pop(L3GD20list)
            List.pop(L3GD20list)
            List.pop(L3GD20list)
            List.pop(L3GD20list)
            List.pop(L3GD20list)
        end
        i2c.start(id)
        i2c.address(id, L3GD20addr ,i2c.TRANSMITTER)
        i2c.write(id,0xA8)
        i2c.stop(id)
        i2c.start(id)
        i2c.address(id, L3GD20addr,i2c.RECEIVER)
        c=i2c.read(id,6)
        i2c.stop(id)
        List.push(L3GD20list,c:sub(1,1))
        List.push(L3GD20list,c:sub(2,2))
        List.push(L3GD20list,c:sub(3,3))
        List.push(L3GD20list,c:sub(4,4))
        List.push(L3GD20list,c:sub(5,5))
        List.push(L3GD20list,c:sub(6,6))
    end
end

function senddata()
    if L3GD20list.items > 95 then
        ghi=""
        for i=1,96 do 
            ghi=ghi..List.pop(L3GD20list)
        end
        sk:send(ghi)
    end
end


List = {}
function List.new ()
    return {first = 0, last = -1, items = 0}
end

function List.push (list, value)
    local last = list.last + 1
    local items = list.items + 1
    list.last = last
    list.items = items
    list[last] = value
end

function List.pop (list)
    local first = list.first
    if first > list.last then error("list is empty") end
    local value = list[first]
    local items = list.items - 1
    list[first] = nil
    list.first = first + 1
    list.items = items
    return value
end


L3GD20list=List.new()
