

module struct_4;

    typedef struct {
        int street;
    } info_t;

    typedef struct {
        int id;
        logic [7:0] age;
        info_t info;
    } person_t;

    person_t person; 
    
    initial begin
        person.id = 1;
        person.age = 30;
        person.info.street = 2;
        
    end
endmodule