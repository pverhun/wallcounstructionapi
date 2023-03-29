"""
WallConstruction Pre-scheduled Multithreading Simulation

"""
import logging
import queue
import time
from .base import BaseWallConstruction, Workload
from threading import Thread
from enum import Enum


class ThreadStatus(Enum):
    AWAITING = 0
    BUSY = 1
    RELIEVED = 2


class TeamWorker(Thread):
    """
    Represents Team worker thread
    """

    def __init__(self, idx: int, w_queue: queue.Queue, logger: logging.Logger, day: int = None):
        """
         :param idx: Team index
         :param w_queue: Workload queue
         :param day: Day to stop work
         :param logger: Worker logger
         """
        self.idx = idx
        self.queue = w_queue
        self.stop_day = day
        self.logger = logger

        self.status: ThreadStatus = ThreadStatus.AWAITING
        self.workload: Workload | None = None
        self.day = 1
        self.current_section_height = 0

        super().__init__()

    def relieve(self, status=ThreadStatus.RELIEVED):
        self.status = status
        self.log(f'[Day - {self.day}] [Team {self.idx}] Relieved.')

        return True

    def log(self, msg: str):
        self.logger.debug(msg)

    def run(self):

        while True:
            if self.status == ThreadStatus.AWAITING:
                try:
                    self.workload = self.queue.get(timeout=0.001)
                except:
                    return self.relieve()

                self.log(f'[Day - {self.day}] [Team {self.idx}] Got workload {self.workload}')
                if self.workload.is_relieve:
                    return self.relieve()

                self.current_section_height = self.workload.section_height
                self.status = ThreadStatus.BUSY

            self.current_section_height += BaseWallConstruction.FOOTS_PER_DAY

            self.log(f'[Day - {self.day}] [Team {self.idx}]  Profile {self.workload.profile + 1}'
                     f' Section {self.workload.section + 1}'
                     f' Height {self.current_section_height}')

            if self.current_section_height == BaseWallConstruction.SECTION_HEIGHT:
                self.log(f'[Day - {self.day}] [Team {self.idx}]  Completed section {self.workload.section + 1} '
                         f'in profile {self.workload.profile + 1}')
                self.status = ThreadStatus.AWAITING
                self.queue.task_done()

            if self.day == self.stop_day:
                return self.relieve(status=self.status)

            self.day += 1


class WallConstructionMt2(BaseWallConstruction):
    """
    Represents Manager thread
    """
    RELIEVE_WORKLOAD = Workload(is_relieve=True)

    def __init__(self, file_input: str, log_file: str = ''):

        f = open(file_input, "r")
        self.available_teams = int(f.readline())

        super().__init__(f)

        if not log_file:
            log_file = f'wallconstruction/logs/mt2/worker_out_{time.time()}.log'

        fileh = logging.FileHandler(log_file, 'w')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fileh.setFormatter(formatter)

        self.worker_logger = logging.getLogger('AsyncWorkerLogger')
        self.worker_logger.setLevel(logging.DEBUG)
        self.worker_logger.addHandler(fileh)

        self.workers_pool = []
        for i in range(self.available_teams):
            self.workers_pool.append(TeamWorker(idx=i, w_queue=queue.Queue(), logger=self.worker_logger))

    def get_wall_costs(self,
                       profile_no: int | None = None,
                       day: int | None = None,
                       accumulate: bool | None = False) -> (int, int):

        processed_volume = 0
        current_day_volume = 0
        profile_no = profile_no - 1 if profile_no else None

        workflow = self.workflow_gen()

        for worker in self.workers_pool:
            worker.stop_day = day
            worker.start()

        # Set workload for available workers
        scheduled = False
        workload_schedule = tuple([] for _ in range(self.available_teams))

        # We need to schedule workload in a way that next workload come to worker which finished section first
        # this is why we need this ordered list of worker indexes every iteration
        ordered_workers_idx = [i for i in range(self.available_teams)]

        while not scheduled:
            # List consist of ordered tuples of worker indexes and section height (worker_idx, section_height)
            ordered_workloads: list[tuple] = []

            for worker_idx in ordered_workers_idx:
                worker = self.workers_pool[worker_idx]
                try:
                    workload = next(workflow)
                    ordered_workloads.append((worker_idx, workload.section_height))
                    workload_schedule[worker.idx].append(workload)
                except StopIteration:
                    scheduled = True
                    break
                worker.queue.put(workload)

            if not ordered_workloads:
                continue

            ordered_workloads.sort(key=lambda x: x[1], reverse=True)
            ordered_workers_idx = [x[0] for x in ordered_workloads]

        # Wait for workers to finish all scheduled jobs
        for worker in self.workers_pool:
            worker.join()

        # Calculate workload costs
        for worker in self.workers_pool:
            worker_workloads = workload_schedule[worker.idx]

            for workload in worker_workloads:

                # Skip workload if requested profile not match workload profile
                if profile_no is not None and profile_no != workload.profile:
                    continue

                section_height_delta = worker.current_section_height - workload.section_height

                if day:
                    if workload.profile == worker.workload.profile and workload.section == worker.workload.section:
                        current_day_volume += self.ICE_VOLUME_PER_FOOT
                        processed_volume += section_height_delta * self.ICE_VOLUME_PER_FOOT
                else:
                    processed_volume += section_height_delta * self.ICE_VOLUME_PER_FOOT

        return (processed_volume, processed_volume * self.COST_PER_ICE_VOLUME) if accumulate else \
            (current_day_volume, current_day_volume * self.COST_PER_ICE_VOLUME)
