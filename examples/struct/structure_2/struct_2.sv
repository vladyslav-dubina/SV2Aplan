module struct_2;

    typedef struct {
        int id;
        logic [7:0] age;
    } person_t;

    person_t person; 
    
    initial begin
        person.id = 1;
        person.age = 30;
        
    end
endmodule