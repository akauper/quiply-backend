from ..base_tool import BaseTool
from .models import PurgeOptions
from firestore import db


class PurgeTool(BaseTool):
    def run_all(self, **kwargs) -> None:
        purge_options: PurgeOptions = kwargs.get('purge_options', PurgeOptions())
        self.purge_scenario_instances(purge_options)
        self.purge_scenario_results(purge_options)
        self.purge_all_actor_templates(purge_options)
        self.purge_all_scenario_templates(purge_options)

    def purge_scenario_instances(self, purge_options: PurgeOptions):
        coll_ref = db.collection('users').document(purge_options.user_id).collection('scenarioInstances')
        self.delete_docs_in_collection(coll_ref, purge_options)

    def purge_scenario_results(self, purge_options: PurgeOptions):
        coll_ref = db.collection('users').document(purge_options.user_id).collection('scenarioResults')
        self.delete_docs_in_collection(coll_ref, purge_options)

    def purge_all_actor_templates(self, purge_options: PurgeOptions):
        coll_ref = db.collection('actorTemplates')
        self.delete_docs_in_collection(coll_ref, purge_options)

    def purge_all_scenario_templates(self, purge_options: PurgeOptions):
        coll_ref = db.collection('scenarioTemplates')
        self.delete_docs_in_collection(coll_ref, purge_options)

    @staticmethod
    def delete_docs_in_collection(coll_ref, purge_options: PurgeOptions):
        batch = db.batch()  # Create a batch
        batch_size = 0

        preserve_recent_count = 0 if purge_options.preserve_recent_count is None else purge_options.preserve_recent_count

        try:
            if preserve_recent_count > 0:
                docs = coll_ref.order_by('updated_at', direction='DESCENDING').stream()
            else:
                docs = coll_ref.stream()

            skipped = 0
            for doc in docs:
                if skipped < preserve_recent_count:
                    skipped += 1
                    continue

                print(f"Queueing doc {doc.id} => {doc.to_dict()} for deletion")
                batch.delete(doc.reference)
                batch_size += 1

                if batch_size >= 500:  # Firebase batch write limit
                    print("Committing batch...")
                    batch.commit()
                    batch = db.batch()
                    batch_size = 0

            if batch_size > 0:
                print("Committing final batch...")
                batch.commit()

        except Exception as e:
            print(e)