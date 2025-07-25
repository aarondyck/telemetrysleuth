------- SEARCH
        try:
            # Store in database
            record_id = self.db_manager.store_call_record(parsed_data)
            
            if record_id:
                logger.info(f"Successfully stored call record with ID: {record_id}")
                self.stats['records_processed'] += 1
                return record_id
            else:
                logger.error("Failed to store call record in database")
                self.stats['parse_errors'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Error storing call record: {e}")
            self.stats['parse_errors'] += 1
            return None
=======
        try:
            # Store in database
            record_id = self.db_manager.store_call_record(parsed_data)
            
            if record_id:
                logger.info(f"Successfully stored call record with ID: {record_id}")
                self.stats['records_processed'] += 1
                
                # Broadcast new record via WebSocket
                try:
                    websocket_manager = get_websocket_manager()
                    # Prepare record data for broadcasting
                    broadcast_data = parsed_data.copy()
                    broadcast_data['id'] = record_id
                    broadcast_data['timestamp'] = datetime.now().isoformat()
                    
                    # Convert datetime objects to ISO format for JSON serialization
                    for key, value in broadcast_data.items():
                        if isinstance(value, datetime):
                            broadcast_data[key] = value.isoformat()
                    
                    websocket_manager.broadcast_new_record(broadcast_data)
                    logger.debug(f"Broadcasted new record {record_id} via WebSocket")
                    
                except Exception as ws_error:
                    logger.warning(f"Failed to broadcast record via WebSocket: {ws_error}")
                
                return record_id
            else:
                logger.error("Failed to store call record in database")
                self.stats['parse_errors'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Error storing call record: {e}")
            self.stats['parse_errors'] += 1
            return None
+++++++ REPLACE