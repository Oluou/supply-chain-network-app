"""
Modular ingestion interface for supply chain network sources.
Each source implements a class with ingest() method returning nodes/edges.
"""
import json
import decimal
from typing import List, Dict, Tuple

class IngestionSource:
    def ingest(self) -> Tuple[List[Dict], List[Dict]]:
        raise NotImplementedError

class USAspendingIngestion(IngestionSource):
    def __init__(self, fy=2023, agency="Department of Defense", limit=10):
        from usaspending import USASpendingClient
        self.fy = fy
        self.agency = agency
        self.limit = limit
        self.client = USASpendingClient()
    def ingest(self) -> Tuple[List[Dict], List[Dict]]:
        g_nodes = {}
        g_edges = []
        def add_node(node_id, node_type, **attrs):
            g_nodes[node_id] = {"id": node_id, "type": node_type, **attrs}
        def add_edge(source, target, edge_type, **attrs):
            g_edges.append({"source": source, "target": target, "type": edge_type, **attrs})
        awards = self.client.awards.search() \
            .agency(self.agency) \
            .contracts() \
            .fiscal_year(self.fy) \
            .order_by("Award Amount", "desc") \
            .limit(self.limit).all()
        for award in awards:
            fa_name = getattr(award.awarding_agency, "name", "Unknown Agency")
            fa_id = f"agency:{fa_name}"
            add_node(fa_id, "funding_agency", name=fa_name)
            prog_office = getattr(award, "awarding_agency", None)
            if prog_office and getattr(prog_office, "subtier_agency", None):
                po_id = f"program:{prog_office.subtier_agency.abbreviation}"
                add_node(po_id, "program_office", name=prog_office.subtier_agency.name, parent=fa_id)
            else:
                po_id = fa_id
            if award.recipient:
                prime_id = f"prime:{award.recipient.duns or award.recipient.uei or award.recipient.name}"
                add_node(prime_id, "prime_contractor", name=award.recipient.name)
                add_edge(po_id, prime_id, "prime_contract", value=award.total_obligation, award_id=award.award_identifier)
                if getattr(award, "subaward_count", 0) > 0:
                    for subaward in award.subawards:
                        if subaward.recipient:
                            sub_id = f"supplier:{subaward.recipient.duns or subaward.recipient.uei or subaward.recipient.name}"
                            add_node(sub_id, "supplier", name=subaward.recipient.name)
                            add_edge(prime_id, sub_id, "subcontract", value=getattr(subaward, "amount", None), subaward_id=getattr(subaward, "subaward_number", None))
        return list(g_nodes.values()), g_edges

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

if __name__ == "__main__":
    # Example usage: modular ingestion
    sources = [USAspendingIngestion()]
    all_nodes, all_edges = [], []
    for src in sources:
        nodes, edges = src.ingest()
        all_nodes.extend(nodes)
        all_edges.extend(edges)
    with open("usaspending_nodes.json", "w") as f:
        json.dump(all_nodes, f, indent=2, default=decimal_default)
    with open("usaspending_edges.json", "w") as f:
        json.dump(all_edges, f, indent=2, default=decimal_default)
    print(f"Extracted {len(all_nodes)} nodes and {len(all_edges)} edges.")
