module struct_1;
    struct {    
        int id;
        logic [7:0] age;
    } person; 
    
    initial begin
        person.id = 1;
        person.age = 30;
        
    end
endmodule