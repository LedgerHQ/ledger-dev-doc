===========================
Advanced display management
===========================

This article talks about more advanced flows that are sometimes needed when writing applications.

Cherry-picking steps at runtime
===============================

Usecase
-------

The :doc:`Display Management </userspace/display_management>` doc taught us how to use the :code:`UX_FLOW` macro. This macro is quite handy but comes with its **drawbacks**: everything needs to be declared at **compilation time**. What if we wished to change the :code:`flow` at runtime?

Imagine an app where you have a flow for a transaction signature.

.. code-block:: c

   UX_FLOW(ux_transaction_signature,
            &step_review,
            &step_amount,
            &step_fee,
            &step_address,
            &step_accept,
            &step_reject
         );

This works well enough for a transaction signature. But suppose there's an update to the protocol: now some transactions can also sign some arbitrary data. However, not all transactions are required to sign the arbitrary data, so you need two flows:

.. code-block:: c

   // The standard signature, nothing has changed.
   UX_FLOW(ux_vanilla_transaction_signature,
            &step_review,
            &step_amount,
            &step_fee,
            &step_address,
            &step_accept,
            &step_reject
         );

   // This flow is almost the same as the one above, except is contains "step_arbitrary_data".
   UX_FLOW(ux_data_transaction_signature,
            &step_review,
            &step_amount,
            &step_fee,
            &step_address,
            &step_arbitrary_data, // Arbitrary data
            &step_accept,
            &step_reject
         );

And now somewhere in your app at runtime you will be able to decide which flow to use:

.. code-block:: c

   void launch_flow() {
      if (g.has_arbitrary_data) {
         ux_flow_init(0, ux_data_transaction_signature, NULL);
      } else {
         ux_flow_init(0, ux_vanilla_transaction_signature, NULL);
      }
   }

Great this works. Hu-oh but now the community also wants to be able to see the nonce for the transaction. But they want it to be optional. You know for *advanced* users.

Ok so back to work: we need a flow for the vanilla signature, as well as a flow for the vanilla signature where we show the nonce. Oh but wait we also need the option to display the nonce when there is arbitrary data to sign, so we **also** need the "data signature" flow **and** the "data signature + nonce" flow.

.. code-block:: c

   // The standard signature, nothing has changed.
   UX_FLOW(ux_vanilla_transaction_signature,
            &step_review,
            &step_amount,
            &step_fee,
            &step_address,
            &step_accept,
            &step_reject
         );

   // Now the vanilla flow where we just add the step to display the nonce.
   UX_FLOW(ux_vanilla_nonce_transaction_signature,
            &step_review,
            &step_amount,
            &step_fee,
            &step_address,
            &step_nonce, // Nonce
            &step_accept,
            &step_reject
         );

   // This is identical to the previous example, where we signed some arbitrary data.
   UX_FLOW(ux_data_transaction_signature,
            &step_review,
            &step_amount,
            &step_fee,
            &step_address,
            &step_arbitrary_data, // Arbitrary data
            &step_accept,
            &step_reject
         );
         
   // This is identical to the flow just above, except we add a step to display the nonce.
   UX_FLOW(ux_data_nonce_transaction_signature,
            &step_review,
            &step_amount,
            &step_fee,
            &step_address,
            &step_arbitrary_data, // Arbitrary data
            &step_nonce, // Nonce
            &step_accept,
            &step_reject
         );

And now somewhere in our app at runtime we're able to decide which flow to use:

.. code-block:: c

   void launch_flow() {
      if (g.has_arbitrary_data) {
         if (g.display_nonce) {
            ux_flow_init(0, ux_data_nonce_transaction_signature, NULL);
         } else {
            ux_flow_init(0, ux_data_transaction_signature, NULL);
         }
      } else {
         if (g.display_nonce) {
            ux_flow_init(0, ux_vanilla_nonce_transaction_signature, NULL);
         } else {
            ux_flow_init(0, ux_vanilla_transaction_signature, NULL);
         }
      }
   }

Ugh. Ok now everyone's happy: we've updated our app to support the protocol and the advanced users in the community can display the nonce.
But now a new upgrade to the protocol is planned for the near future: the fees can sometimes be paid by another user of the blockchain, called a relayer. Anyways now some transactions now need to **hide** the fees (displaying a fee of 0.000 is not an option because it would confuse users more than anything).

So we need... **8 different flows**. That escalated quickly! Indeed, for every little *upgrade*, we're doubling the number of flows. Soon enough we'll end up with 16 or even 32 different flows... Notice that whilst the number of flows will grow exponentially, the number of different steps though will only grow linearly (one for every new feature).

To fix this problem, we would need to define the UX_FLOW at runtime, cherry-picking which steps we wish to include depending on the details of our transaction.

Don't worry, Ledger's got your back! The fix is quite simple, so let's dive right into it!

Cherry-picking explained
------------------------

The idea is to create an array of steps that would be big enough to fit all the steps. Since steps grow linearly, this array won't be too big.
Once this array created, we simply need to fill it with the steps we wish to include. Finally, we need to add a last step :code:`FLOW_END_STEP` for it to work properly.

We can then call the :code:`ux_init_flow` and pass in our array as argument!

.. code-block:: c

   // The maximum number of steps we will ever need. Here it's 8: step_review, step_amount,
   // step_fee, step_address, step_arbitrary_data, step_nonce, step_accept, step_reject.
   #define MAX_NUM_STEPS 8

   // The array of steps. Notice the type used, as it's important if you wish to use ux_init_flow.
   // We're adding `+ 1` because we need to ensure we always have extra room for the last step, FLOW_END_STEP.
   const ux_flow_step_t *ux_signature_flow[MAX_NUM_STEPS + 1];

.. code-block:: c

   void start_display() {
      uint8_t index = 0;

      // Set the first step to be `step_review`, and then increment `index`.
      ux_signature_flow[index++] = step_review;
      // Set the second step to be `step_amount`, and then increment `index`.
      ux_signature_flow[index++] = step_amount;
      // etc...
      ux_signature_flow[index++] = step_fee;
      ux_signature_flow[index++] = step_address;
      // We can now conditionally add steps at runtime!
      if (g.has_arbitrary_data) {
         ux_signature_flow[index++] = step_arbitrary_data;
      }
      if (g.display_nonce) {
         ux_signature_flow[index++] = step_nonce;
      }
      ux_signature_flow[index++] = step_accept;
      ux_signature_flow[index++] = step_reject;

      // Don't forget to finish your flow with this special step.
      ux_signature_flow[index++] = FLOW_END_STEP;

      // Start the display!
      ux_init_flow(0, ux_signature_flow, NULL);
   }



Defining steps at runtime
=========================

Usecase
-------

In the previous section we saw that we could define a :code:`UX_FLOW` at runtime. But we did this whilst still having steps defined statically. What if we wish to define steps at runtime too? This would give us a very fine-grained control over what we wish to display, without having to declare a step everytime.

We'd encounter two main issues:

#. What globals are we going to need? Previously, we would have defined :code:`global.amount` to store the amount to display, :code:`global.fees` to store the fees to display, :code:`global.address` to store the address we wish to display, etc. Prior to calling the display function, we would've pre-computed all of that data, and then every :code:`step` would've simply looked at those :code:`global.*` fields to display their data. But how can do that now, given that we don't know how many steps we are going to use?
#. How would we define the :code:`UX_FLOW`? We literally used to specify :code:`step1`, :code:`step2`, :code:`step3` etc... Can we create a generic step that would replace those? A :code:`step_generic` step?

Let's try and address both of these problems: the **Data Storage** (1) problem and then the **UX declaration** (2) problem.

Data Storage
------------

Here's what the code for a typical transaction would look like.
It consists of a global struct that contains all the data we need, and a function (:code:`prepare_then_display_transaction`) that will compute all the necessary data and store it in our global, and then call the appropriate flow to display those.

In the :code:`.h` file

.. code-block:: c

   // Our global object that is accessible anywhere
   struct global {
      // display struct where we will store the strings we wish to display
      struct display {
         char fees[MAX_FEE_LENGTH];
         char amount[MAX_AMOUNT_LENGTH];
         char address[MAX_ADDRESS_LENGTH];
      };
      // Other unrelated fields left out.
   };

In the :code:`.c` file:

.. code-block:: c

   // Function called to load all the data and to display the transaction flow.
   void prepare_then_display_transaction() {
      // Computes the string representation of `fee` and copies it to `&global.display.fee`.
      fees_to_str(&global.display.fee, &global_data.fee);
      // Computes the string representation of `amount` and copies it to `&global.display.amount`.
      amount_to_str(&global.display.amount, &global_data.amount);
      // Computes the string representation of a `pubkey` and copies it to `&global.display.address`.
      pubkey_to_str(&global.display.address, &global_data.pubkey);

      // Start the display!
      ux_flow_init(0, static_flow, NULL); // static_flow is defined elsewhere.
   }


There's something **key to notice** here: the **shape of the functions** we're using to compute the string representation.
They all have the same structure: **first argument** is where we wish to **copy it**, the **second** is a **pointer to the data it's going to use**.

Eureka! To print a single step, we only need three different pieces of information:

#. The function that will convert our data to a string.
#. The data we wish to convert.
#. The "title" we wish to display (e.g. "Fee", or "Amount", or "Address"...).

These can all fit in a struct, that we will name :code:`step_info_t`.

To create a list of screens, we only need to store a list of :code:`step_info_t`.
Even though we might not know **exactly** how many steps we will be needing at runtime, we can probably set a pretty good **upper bound** to the total number of screens we might need for a single flow.

In the :code:`.h` file:

.. code-block:: c

   // Maximum size of any data
   #define MAX_DATA_SIZE MAX(MAX_FEE_LENGTH, MAX_AMOUNT_LENGTH, MAX_ADDRESS_LENGTH)
   // Maximum number of steps we might ever need in a single flow.
   // Adding one because we need to account for the last FLOW_STEP_END.
   #define MAX_STEP_COUNT 7 + 1
   // Number of characters we can draw on the screen without overflowing.
   // Adding one because we need to account for the null terminating character.
   #define PROMPT_WIDTH 15 + 1

   // A typedef that corresponds to a function pointer that will generate the appropriate string, given some data.
   // e.g `fees_to_str`, `amount_to_str`, or `pubkey_to_str`
   typedef void (*string_generating_fn);

   // A struct that contains every pieces of information to display a single step.
   struct step_info_t {
      // This will get filled by the title.
      char title[PROMPT_WIDTH];
      // This is a pointer to the data we need to generate the string.
      void *data;
      // A function pointer that we will call on `data`.
      string_generating_fn fn;
   };

   struct global {
      // Memory location where we will copy the title for each screen.
      char                 title[PROMPT_WIDTH];
      // Memory location where we will copy the string representation of the data we wish to print.
      char                 text[MAX_DATA_SIZE];
      // Array of `step_info_t` which represents all the steps we wish our flow to have.
      struct step_info_t   display_arr[MAX_STEP_COUNT];
      // Current index on the array `display_arr` array.
      uint8_t              current_index;
      // Total size of the `display_arr` array (should be less than MAX_STEP_COUNT).
      uint8_t              total_size;
      // Other unrelated fields left out.
   };

Now that we have the struct and :code:`define` s, we need to implement the business logic.
We will need two functions: :code:`push_step` that will add a step to our :code:`step_array`. Another function  :code:`step_array_display` will display the :code:`step_array`. In the code below, an example of :code:`display_transaction` is also given, to show you how those functions should be used.

In the :code:`.c` file:

.. code-block:: c

   // Utility function to push steps on the step array.
   void push_step(char *title, void *data, string_generating_fn convert_fn) {
      if (global.curr_size) >= MAX_STEP_COUNT {
         // Don't add steps if we're already passed MAX_STEP_COUNT.
         return;
      }

      // The chosen step data.
      struct step_info_t *step_info = global.display_arr[curr_size];

      strcpy(step_info->title, title);
      step_info->data = data;
      step_info->fn = convert_fn;

      // Don't forget to increment the current size!
      global.curr_size++;
   }

   // Call this function once you've added the correct steps on the array.
   void step_array_display() {
      // We need to keep track of the total_size somewhere in order not to go out of bounds when navigating through the array.
      global.total_size = global.curr_size;
      // Reset the current size to 0, so that we start by displaying the first screen.
      gobal.curr_size = 0;

      // Start the flow!
      ux_flow_init(0, dynamic_flow, NULL); // `dynamic_flow` has not been defined yet, we'll see this in the next section!
   }

   // This is an example of how these functions should be called.
   void display_transaction() {
      // Reset the current size to 0 to make sure we start from the beginning of the array.
      global.curr_size = 0;
      // Push a step that will display the amount.
      step_array_push("Amount", &global_data.amount, &amount_to_str);
      // Push a step that will display the fee.
      step_array_push("Fee", &global_data.fee, &fee_to_str);
      // Push a step that will display the address.
      step_array_push("Address", &global_data.address, &pubkey_to_str);

      // Start the display.
      step_array_display();
   }

Now that we've solved (1), we need to solve (2) which is the *UX declaration problem*. How do we need to adapt our flows to accomodate for our new steps?

UX declaration problem
----------------------

Now comes the difficult part. Finding a step that would be generic enough to fit all our needs. Naively, the code we'd expect would look something like that:

.. code-block:: c

   // Naive definition of a UX_FLOW.
   // Note: we are still keeping step_review, step_accept and
   // step_reject because we know our flow will need those anyway.
   UX_FLOW(ideal_dynamic_fow,
            &step_welcome,
            &step_generic, // A generic step that would fit all our needs.
            &step_quit
            FLOW_LOOP
      );


However this wouldn't work: if we only defined a single step, then how could it dynamically change its information? Pressing the right button would  make it loop and we'd end up on the same exact screen, and pressing the left button would lead to the same situation.

So here's a solution:

* Add an extra step just before the :code:`step_generic` step, and another one right after it.
* Those extra steps are nothing but delimiters for the :code:`step_generic` . They allow us to execute special logic to update the screen and redisplay it. They also allow us to keep track of an index, so that we know whether we're still within our array boundaries or not.

Here's what the code looks like.

.. code-block:: c

   UX_FLOW(dynamic_flow,
            &step_welcome,

            &step_upper_delimiter, // A special step that serves as the upper delimiter. It won't print anything on the screen.
            &step_generic, // Our generic step that will actually display stuff on the screen.
            &step_lower_delimiter, // A special step that serves as the lower delimiter. It won't print anything on the screen.

            &step_quit,
            FLOW_LOOP
      );

The definition of :code:`step_upper_delimiter`, :code:`step_lower_delimiter` and :code:`step_generic` could look like this:

.. code-block:: c
   

   // Note we're using UX_STEP_INIT because this step won't display anything.
   UX_STEP_INIT(
      step_upper_delimiter,
      NULL,
      NULL,
      {
         // This function will be detailed later on.
         display_next_state(true);
      }
   );

   UX_STEP_NOCB(
      step_generic,
      bnnn_paging,
      {
         .title = global.title,
         .text = global.text,
      }
   );

   // Note we're using UX_STEP_INIT because this step won't display anything.
   UX_STEP_INIT(
      step_lower_delimiter,
      NULL,
      NULL,
      {
         // This function will be detailed later on.
         display_next_state(false);
      }
   );

As you can see, :code:`step_upper_delimiter` and :code:`step_lower_delimiter` are very similar. :code:`step_generic` is a simple :code:`bnnn_paging` that will always display what's located in :code:`global.title` and :code:`global.text`.

And now we only need to  implement the special logic for this to work!


Inside the :code:`.h` file, we just need to add an enum definition and an instance of this enum in our global structure:

.. code-block:: c

   // State of the dynamic display.
   // Use to keep track of whether we are displaying screens that are inside the 
   // array (dynamic), or outside the array (static).
   enum e_state {
      STATIC_SCREEN,
      DYNAMIC_SCREEN,
   };

   struct global {
      // An instance of our new enum
      enum e_state current_state;

      // The rest of the global stays unchanged...
   }

And in the :code:`.c` file, we add all the business logic. The code is commented thoroughly, so take your time and read it carefully.

.. code-block:: c

   // Utility function to clear the title and the text fields.
   void clear_data() {
      explicit_bzero(&global.title, sizeof(global.title));
      explicit_bzero(&global.text, sizeof(global.text));
   }

   // Updates the global.title and global.text with the current `step_info_t` pointed to by the `current_size`.
   void set_step_data() {
      // Start by clearing the data for extra safety.
      clear_data();
       
      // Select the current step_info.
      struct step_info_t *step_info = &global.display_arr[global.current_index];
      
      // Copy the title located in the step_info to the global title.
      strcpy((char *)global.title, step_info->title);

      // Call the `string_generating_fn` on the data contained in the step_info,
      // and store the string in the global.text.
      step_info->fn(&global.text, sizeof(global.text), step_info->data);
   }

   // This is a special function we must call for bnnn_paging to work properly in an edgecase.
   // It does some weird stuff with the `G_ux` global which is defined by the SDK.
   // No need to dig deeper into the code, a simple copy paste will do.
   void bnnn_paging_edgecase() {
       G_ux.flow_stack[G_ux.stack_count - 1].prev_index = G_ux.flow_stack[G_ux.stack_count - 1].index - 2;
       G_ux.flow_stack[G_ux.stack_count - 1].index--;
       ux_flow_relayout();
   }

   // Main function that handles all the business logic for our new display architecture.
   void display_next_state(bool is_upper_delimiter) {
      if (is_upper_delimiter) { // We're called from the upper delimiter.
         if (global.current_state == STATIC_SCREEN) {
            // The previous screen was a static screen, so we're now entering the array (from the start of the array).

               // Since we're in the array, set the state to DYNAMIC_SCREEN.
               global.current_state = DYNAMIC_SCREEN;
               // We're just entering the array so set the `current_index` to 0.
               global.current_index = 0;
               // Update the screen data.
               set_screen_data();
               // Move to the next step, which will display the screen.
               ux_flow_next();
            } else {
               // The previous screen was NOT a static screen, so we were already in the array.
               if (global.current_index == 0) {
                  // If `current_index` is 0 then we need to exit the dynamic display.

                  // Update the current_state accordingly.
                  global.current_state = STATIC_SCREEN;
                  // Don't need to update the screen data, simply display the ux_flow_prev() which
                  // will be a static screen.
                  ux_flow_prev();
               } else {
                  // global.current_index is not 0 which means the user is still browsing the array.

                  // Decrement `current_index` since the user has pressed the left button meaning
                  // he wants to see the previous screen.
                  global.current_index--;
                  // Update the screen data.
                  set_screen_data();
                  // Move to the next step which will display the updated.
                  ux_flow_next();
               }
            }
         } else {
           // We're called from the lower delimiter.

           if (global.current_state == STATIC_SCREEN) {
               // We're called from a static screen, so we're now entering the array (from the end of the array).

               // Update the current_state.
               global.current_state = DYNAMIC_SCREEN;
               // We're starting the array from the end, so the index is the size - 1.
               global.current_index = global.total_size - 1;
               // Update the screen data.
               set_screen_data();
               // Since we're called from the RIGHT ux step, if we wish to display
               // the data we need to call ux_flow_PREV and not `ux_flow_NEXT`.
               ux_flow_prev();
           } else {
               // We're being called from a dynamic screen, so the user was already browsing the array.

               // The user wants to go to the next screen so increment the index.
               global.current_index++;

               if (global.current_index == global.total_size) {
                  // Index is equal to array size, so time to exit the array and display the static screens.

                  // Make sure we update the state accordingly.
                  global.current_state = STATIC_SCREEN;

                  // Display the next screen
                  ux_flow_next();
               } else {
                  // The user is still browsing the array so update the screen and display it.
                  set_screen_data();

                  // Similar to `ux_flow_prev()` but updates layout to account for `bnnn_paging`'s weird behaviour.
                  bnnn_paging_edgecase();
               }
            }
         }
      }

That was a mouthful! But we did it: we managed to dynamically adapt our flow AND our steps!