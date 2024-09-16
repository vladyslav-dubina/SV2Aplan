module example_size();
    // Declare different types of arrays
    int static_array[5];  // Static array with 5 elements
    int dynamic_array[];  // Dynamic array
    int queue[$];         // Queue

    initial begin
        // Initialize the static array
        static_array[0] = 10;
        static_array[1] = 20;
        static_array[2] = 30;
        static_array[3] = 40;
        static_array[4] = 50;

        // Initialize the dynamic array
        dynamic_array = new[3];  // Set the size to 3
        dynamic_array[0] = 100;
        dynamic_array[1] = 200;
        dynamic_array[2] = 300;

        // Initialize the queue
        queue.push_back(5);
        queue.push_back(15);
        queue.push_back(25);

        // Print the sizes of the arrays
        $display("Size of static_array: %0d", $size(static_array));  // Output: 5
        $display("Size of dynamic_array: %0d", $size(dynamic_array));  // Output: 3
        $display("Size of queue: %0d", $size(queue));  // Output: 3
    end
endmodule