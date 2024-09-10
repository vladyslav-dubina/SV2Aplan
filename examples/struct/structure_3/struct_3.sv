typedef struct {
    int id;
    logic [7:0] age;
} person_t;

module struct_3;
    person_t person; 
    
    initial begin
        person.id = 1;
        person.age = 30;
        
    end
endmodule