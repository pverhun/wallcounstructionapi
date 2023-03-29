### Wall Construction API



### Solution  
There are 2 general ways to implement such program:
 * Make all calculations save it somewhere and then return the data based on requested params.
 * Lazy calculation, means that calculation will stop and result returned when requested params have been reached.

I decided to implement a lazy method because it is more challenging and requires less computing resources. 
I came up with 3 lazy solutions:

 * Calculations in one thread.
 * Multithreaded.
 * Multithreaded pre-scheduled.

### Calculations in one thread
    Script Location: api/wallconstruction/modules/wall_construction/basic.py 
    
    Input files location: api/wallconstruction/modules/wall_construction/inputs
    
    Tests: api/wallconstruction/modules/wall_construction/tests/basic_test.py
 
 Just basic lazy calculations in one thread.


### Multithreaded
    Script Location:  api/wallconstruction/modules/wall_construction/mt_async.py 
    
    Input files location: api/wallconstruction/inputs/mt
    
    Tests: api/wallconstruction/modules/wall_construction/tests/mt_async_test.py
    
    Log files: api/wallconstruction/logs/mt_async


We have Manager which is also main thread, workload Queue and Team Workers.  
Lazy Async simulation works fast but a bit harder to understand and modify.

* #### Manager 
    - Feed workload Queue with Workload object consist of wall section's indexes.  
    - Counting costs when all tasks completed OR stop day reached.  
    - Send RELIEVE task if no workload available.  

* #### Queue
    - Consist of Workload objects which are fed from Manager.  
    - Workload object locate concrete wall section.

* #### Team Worker
    - Worker counting days himself.  
    - Draining Queue get workload and become in 'BUSY' state until wall section will be completed OR stop day reached.  
    - Once section completed worker switch to 'AWAITING' state and wait for the new Workload.  
    - Worker in 'BUSY' state didn't drain Queue and building current section.


### Multithreaded Pre-scheduled
    Script Location:  api/wallconstruction/modules/wall_construction/mt_async2.py 
    
    Input files location: api/wallconstruction/inputs/mt
    
    Tests: api/wallconstruction/modules/wall_construction/tests/mt_async2_test.py
    
    Log files: api/wallconstruction/logs/mt_async


We have Manager which is also main thread, workload Queue and Team Workers.  
Lazy Async simulation works fast but require more memory.

* #### Manager 
    - Schedule workload Queue with Workload object consist of wall section's indexes.  
    - Counting costs when all tasks completed.

* #### Queue
    - Consist of Workload objects which are fed from Manager.  
    - Workload object locate concrete wall section.

* #### Team Worker
    - Worker counting days himself.  
    - Draining Queue get workload and become in 'BUSY' state until wall section will be completed OR stop day reached.
    - Worker in 'BUSY' state didn't drain Queue and building current section.

### Run API
    pip install -r requirements.txt
    cd api
    python manage.py migrate
    python manage.py runserver

There is additional 'v' query parameter to define implementation which will be used to calculate wall construction.  

For example   

    /profiles/overview/?v=mt

Values:  
mt - Multithreaded  
mt2 - Multithreaded pre-scheduled 

If 'v' is not specified the basic implementation will be used.
