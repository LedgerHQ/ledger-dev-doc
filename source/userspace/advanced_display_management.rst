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

In the previous section we saw that we could define a :code:`UX_FLOW` at runtime. But we did this whilst still having steps defined statically. What if we wish to define steps at runtime too? This would give us a very fine-grained control over what we wish to display, without having to declare a step everytime.

Finding a step that would be generic enough to fit all our needs. Naively, the code we'd expect would look something like that:

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

Inside the :code:`.h` file, we only need to add an enum definition and an instance of this enum in our global structure:

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

And in the :code:`.c` file, we add all the business logic. A helper function

.. code-block: c

    bool get_next_data(char *title_buffer, char *text_buffer, bool forward);

is used throughout the code. This function is yours to define, and basically fills the title_buffer and the text_buffer with the appropriate strings. Is returns a :code:`bool` corresponding to whether or not it found data to fill the buffers. The `:code:`bool forward` parameter is used to indicate whether we wish to display the next screen or the previous screen.

 The code is commented thoroughly, so take your time and read it carefully.

.. code-block:: c

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
                // Fetch new data.
                bool dynamic_data = get_next_data(&global.title, &global.text, true);

                if (dynamic_data) {
                    // We found some data to display so we now enter in dynamic mode.
                    global.current_state = DYNAMIC_SCREEN;
                }

                // Move to the next step, which will display the screen.
                ux_flow_next();
            } else {
                // The previous screen was NOT a static screen, so we were already in a dynamic screen.

                // Fetch new data.
                bool dynamic_data = get_next_data(&global.title, &globa.text, false);
                if (dynamic_data) {
                    // We found some data so simply display it.
                    ux_flow_next();
                }
                else {
                    // There's no more dynamic data to display, so 
                    // update the current state accordingly.
                    global.current_state = STATIC_SCREEN;

                    // Display the previous screen which should be a static one.
                    ux_flow_prev();
                }
            } else {
                // We're called from the lower delimiter.

                if (global.current_state == STATIC_SCREEN) {
                    // Fetch new data.
                    bool dynamic_data = get_next_data(&global.title, &global.text, false);

                    if (dynamic_data) {
                        // We found some data to display so enter in dynamic mode.
                        global.current_state = DYNAMIC_SCREEN;
                    }

                    // Display the data.
                    ux_flow_prev();
                } else {
                    // We're being called from a dynamic screen, so the user was already browsing the array.

                    // Fetch new data.
                    bool dynamic_data = get_next_data(&global.title, &global.text, true);
                    if (dynamic_data) {
                        // We found some data, so display it.
                        // Similar to `ux_flow_prev()` but updates layout to account for `bnnn_paging`'s weird behaviour.
                        bnnn_paging_edgecase();
                    } else {
                        // We found no data so make sure we update the state accordingly.
                        global.current_state = STATIC_SCREEN;

                        // Display the next screen
                        ux_flow_next();
                    }
                }
            }
        }
    }

That was a mouthful! But we did it: we managed to dynamically adapt our flow AND our steps!