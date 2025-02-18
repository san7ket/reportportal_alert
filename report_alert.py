import argparse
import logging
from typing import Dict, List
from tabulate import tabulate
from config_module import Config
from cache_module import reset_cache, save_cache, load_cache
from report_portal_client import ReportPortalClient

logging.basicConfig(level=logging.INFO)

def prepare_filters(args) -> Dict[str, str]:
    filters = {}
    if args.name:
        filters['filter.!cnt.name'] = args.name  # Updated to exclude launches by name
    if args.status:
        filters['filter.eq.status'] = args.status
    if args.tags:
        filters['filter.cnt.tags'] = args.tags
    if args.start_from:
        filters['filter.gte.startTime'] = args.start_from
    if args.start_to:
        filters['filter.lte.endTime'] = args.start_to
    if args.attr:
        attr_key, attr_value = args.attr.split('=', 1)
        filters['filter.has.compositeAttribute'] = f"{attr_key}:{attr_value}"
    logging.info(f"Filters being applied for launches: {filters}")
    return filters

def main():
    parser = argparse.ArgumentParser(description="ReportPortal Alert Script")
    parser.add_argument('project_name', help="Project name (e.g., PROW)")
    parser.add_argument('-n', '--name', help="Name filter to exclude")
    parser.add_argument('-tn', '--test-name', help="Test name filter")
    parser.add_argument('--reset-cache', action='store_true', help="Reset cached data")
    parser.add_argument('--status', help="Status filter")
    parser.add_argument('--tags', help="Tags filter")
    parser.add_argument('--start-from', help="Start time filter (YYYY-MM-DD)")
    parser.add_argument('--start-to', help="End time filter (YYYY-MM-DD)")
    parser.add_argument('--attr', help="Attribute filter (key=value)")
    parser.add_argument('--no-verify', action='store_true', help="Disable SSL verification")
    parser.add_argument('--config', default="config.json", help="Path to configuration file")
    args = parser.parse_args()

    if args.reset_cache:
        reset_cache()

    config = Config(config_file=args.config)
    verify_ssl = not args.no_verify if args.no_verify else config.verify_ssl

    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    client = ReportPortalClient(
        base_url=config.base_url,
        token=config.token,
        verify_ssl=verify_ssl
    )

    # Prepare filters for server-side filtering
    filters = prepare_filters(args)

    # Fetch all valid launch IDs dynamically
    try:
        launch_ids = client.fetch_launch_ids(args.project_name, filters)
        if not launch_ids:
            logging.error("No launches found for the project.")
            return
        logging.info(f"Found launch IDs: {launch_ids}")
    except Exception as e:
        logging.error(f"Error fetching launch IDs: {e}")
        return

    cache = load_cache()

    try:
        results_table = []
        total_failed_tests = 0
        total_failed_suites = 0  # Counter for failed suites
        total_failed_launches = 0  # Counter for launches with failures

        for launch_id in launch_ids:
            suites = client.fetch_suites(args.project_name, launch_id)
            launch_has_failures = False

            for suite in suites:
                suite_id = suite['id']
                failed_tests = client.fetch_tests(args.project_name, launch_id, suite_id, test_name_filter=args.test_name)

                if failed_tests:
                    launch_has_failures = True
                    total_failed_suites += 1
                    logging.info(f"Suite {suite_id} has {len(failed_tests)} failed tests.")
                    total_failed_tests += len(failed_tests)
                    for test in failed_tests:
                        test_url = f"{client.base_url}/ui/#{args.project_name}/launches/all/{launch_id}/{suite_id}/{test['id']}/log"
                        results_table.append([suite['name'], test['name'], test['status'], test_url])
                    cache[suite_id] = {
                        "name": suite['name'],
                        "failed_tests": failed_tests
                    }

            if launch_has_failures:
                total_failed_launches += 1

        if results_table:
            print(tabulate(results_table, headers=["Suite Name", "Test Name", "Status", "Test URL"], tablefmt="grid"))
            print(f"\nTotal Failed Tests: {total_failed_tests}")
            print(f"Total Suites with Failures: {total_failed_suites}")
            print(f"Total Launches with Failures: {total_failed_launches}")
        else:
            print("No failed tests found.")

        save_cache(cache)
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()