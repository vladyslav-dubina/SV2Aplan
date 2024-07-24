class Person;
    int index;
    int age;

    function new(int init_index, int init_age);
        index = init_name;
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

    initial begin
        p = new(1, 30);

        p.print_info();

        p.set_age(31);
    end

endmodule
