class Person;
    int index;
    int age;

    function new(int init_index, int init_age);
        index = init_index;
        age = init_age;
    endfunction

    function void set_age(int new_age);
        age = new_age;
    endfunction

    function int get_age();
        return age;
    endfunction

endclass

module main;
    Person p;

    int age;

    initial begin
        p = new(1, 30);


        p.set_age(31);

        age = p.get_age();
    end

endmodule
