1.  Install:

    1.1 Create virtual environment:

        py -3 -m venv venv

    1.2. Copy .env_template into file .env and adjust its content (configuration) as you need.

2.  Run in development mode:

    2.1 Activate virtual environment:

        venv\Scripts\activate

    2.2 Upgrade pip:

        python -m pip install --upgrade pip

    2.3 Install dependencies:

        pip install -r requirements.txt

    2.4 Run web server

        uvicorn main_web:app  # default on 127.0.0.1:8000
        uvicorn main_web:app --host=192.168.8.100 --port=8080

    2.5 Check app running. SWAGGER

        http://127.0.0.1:8000/docs
        
    2.6 Run Celery worker

        celery -A main_celery.app worker --pool=solo --loglevel=info
        celery -A main_celery.main.app worker --pool=solo --loglevel=debug

3.  Generate dependencies file then manually copy required dependencies to requirements.txt:

    pip freeze > requirements_tmp.txt

P.  Profiling

    P.1 Visualization

        use visualizer for generated cprofile files (e.g. snakeviz)

    P.2 Profile any python code

        ```
        import cProfile

        pr = cProfile.Profile()
        pr.enable()

        {code...}

        pr.disable()

        pr.print_stats(sort={sort_key}) # to print report to console

        pr.dump_stats({report_file_path}) # to save report to file
        ```

        or with cli:

        ```
        python -m cProfile -o {report_file_path} {python_script_path}
        ```

